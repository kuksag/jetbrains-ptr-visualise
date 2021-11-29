#!/usr/bin/env python

import lldb
import attr
from time_logger import log_time

PATH_TO_MAPS = '/proc/{}/maps'
OUTPUT_PATTERN = '"{ptr_name}" points to object "{obj_name}", that located in "{func_name}", frame #{frame_id}, ' \
                 'of thread #{thread_id} '


def read_location(location):
    """
    Trying to cast location from "proc/{PID}/maps" to int
    e.g 7f000d417000 -> int(...)

    :param location: string in hex form
    :return: int or None
    """
    try:
        return int(location, 16)
    except ValueError:
        return None


@attr.s()
class TraceInfo:
    """
    Holds info after calling trace_var(pointer, var)
    Can build a name of the target-object
    """
    thread = attr.ib(validator=attr.validators.instance_of(lldb.SBThread))
    frame = attr.ib(validator=attr.validators.instance_of(lldb.SBFrame))
    trace = attr.ib(validator=attr.validators.instance_of(list))
    pointer = attr.ib(validator=attr.validators.instance_of(int))

    def get_offset(self):
        offset = self.pointer - read_location(self.trace[-1].location)
        assert offset >= 0
        return offset

    def build_name_from_trace(self):
        result = ''
        for var in self.trace:
            result += var.name
            if var.num_children > 0 and not var.type.IsArrayType() and var != self.trace[-1]:
                result += '.'
        return result

    @staticmethod
    def get_info(trace_info, ptr_name=None):
        if trace_info:
            return OUTPUT_PATTERN.format(ptr_name=ptr_name or trace_info.pointer,
                                         obj_name=trace_info.build_name_from_trace() + (
                                             f" (offset +{trace_info.get_offset()})" if trace_info.get_offset() else ""),
                                         func_name=trace_info.frame.name,
                                         frame_id=trace_info.frame.idx,
                                         thread_id=trace_info.thread.idx)
        else:
            return f'target not found for'


def get_threads_with_range(process: lldb.SBProcess):
    """
    Gets range of stack for every thread in the process

    :param process: current process running
    :return: list of tuples (lldb.SBThread, (left, right))
    """
    threads = sorted(process.threads, key=lambda x: x.frames[0].sp)
    ranges = []
    id = 0
    with open(PATH_TO_MAPS.format(process.id), 'r') as maps:
        for line in maps:
            # parse '0x12-0x34 56 78' to (0x12, 0x34) and cast to base 10
            left, right = list(map(lambda x: int(x, 16), line.split()[0].split('-')))
            if id < len(threads) and left <= threads[id].frames[0].sp <= right:
                assert left <= right
                ranges.append((left, right))
                id += 1
    return list(zip(threads, ranges))
# TODO: not working when we hit "continue"; need a proper caching
cached_thread_with_ranges = 0


def trace_var(pointer, var: lldb.SBValue, pointee_type: lldb.SBType = None, allow_padding=False):
    """
    If var is not a struct or array, then return it.
    Otherwise, look through all members of var and go inside at which pointer points.

    :param pointer:
    :param var: current var that we look at
    :param pointee_type: pointee_type or None
    :raises ValueError:
    :return: list of lldb.SBValue
    """
    if var.num_children > 0 and not var.type.is_pointer and var.type != pointee_type:
        for child in var.children:
            location = read_location(child.location)
            if not location:
                continue
            try:
                if location <= pointer < location + child.size:
                    return [var] + trace_var(pointer, child, pointee_type)
            except RuntimeError:
                # The wrong type was chosen; e.g. union
                pass
            except AssertionError:
                # Gotta find object without offset
                pass
        # Didnt find any corresponding member => the pointee is in the padding
        if not allow_padding:
            assert pointer == read_location(var.location)
        return [var]
    else:
        if pointee_type is not None and pointee_type != var.type:
            raise RuntimeError(f"pointer type {pointee_type} doesn't match with found type {var.type}")
        return [var]


@log_time
def trace_pointer(pointer, process: lldb.SBProcess, pointee_type: lldb.SBType = None):
    """
    Finding thread, stack, function, object to which the pointer points

    :param pointer: pointer (that may be invalid) to object
    :param process: current process running
    :param pointee_type: pointee_type or None
    :return: TraceInfo or None
    """
    global cached_thread_with_ranges
    if pointee_type and pointee_type.name == 'void':
        pointee_type = None
    if isinstance(cached_thread_with_ranges, int):
        cached_thread_with_ranges = get_threads_with_range(process)
    for thread, (left, right) in cached_thread_with_ranges:
        if not (left <= pointer <= right):
            continue
        for frame in thread.frames:
            # frames goes in stack in from greater to smaller order
            # pass every single, which frame pointer is smaller than our pointer
            if frame.GetFP() < pointer:
                continue
            for var in frame.vars:
                location = read_location(var.location)
                if not location:
                    continue
                if location <= pointer < location + var.size:
                    try:
                        trace = trace_var(pointer, var, pointee_type)
                    except AssertionError:
                        trace = trace_var(pointer, var, pointee_type, allow_padding=True)
                    return TraceInfo(thread=thread,
                                     frame=frame,
                                     pointer=pointer,
                                     trace=trace)
    return None


def tp(debugger, command, exe_ctx, result, internal_dict):
    """
    Alias for call from debugger
    """
    # trace_info = trace_pointer(read_location(command), exe_ctx.GetProcess())
    trace_info = trace_pointer(int(command), exe_ctx.GetProcess())
    print(TraceInfo.get_info(trace_info), file=result)


@log_time
def visualise_pointers(debugger, command, exe_ctx, result, internal_dict):
    """
    Take all pointers from current frame and find their target
    """
    pointers = list(filter(lambda x: x.type.is_pointer, exe_ctx.GetFrame().vars))
    pointers = list(map(lambda x: (x.data.uint64s[0], x.GetName(), x.type.GetPointeeType()), pointers))
    for pointer, ptr_name, pointee_type in pointers:
        trace_info = trace_pointer(pointer, exe_ctx.GetProcess(), pointee_type)
        print(TraceInfo.get_info(trace_info, ptr_name), file=result)


def __lldb_init_module(debugger, internal_dict):
    # command script import python_code/script.py
    debugger.HandleCommand('command script add -f script.visualise_pointers vp')
    debugger.HandleCommand('command script add -f script.tp tp')
