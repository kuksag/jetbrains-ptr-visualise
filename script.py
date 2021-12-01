#!/usr/bin/env python

import lldb
import attr
from time_logger import log_time

PATH_TO_MAPS = '/proc/{}/maps'
OUTPUT_PATTERN = '"{ptr_name}" points to object "{obj_name}", that located in "{func_name}", frame #{frame_id}, ' \
                 'of thread #{thread_id} '


def read_location(location):
    """
    Trying to cast location from "proc/{PID}/maps" to int or None
    e.g 7f000d417000 -> int(...)
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


def get_threads_with_ranges(process: lldb.SBProcess):
    """
    Gets range of stack for every thread in the process.
    """
    threads = sorted(process.threads, key=lambda x: x.GetFrameAtIndex(0).sp)
    ranges = []
    with open(PATH_TO_MAPS.format(process.id), 'r') as maps:
        for thread in threads:
            for line in maps:

                # parse '0x12-0x34 56 78' to (0x12, 0x34) and cast to base 10
                left, right = list(map(lambda x: int(x, 16), line.split()[0].split('-')))
                assert left <= right

                if left <= thread.GetFrameAtIndex(0).sp <= right:
                    ranges.append((left, right))
                    break
    return threads, ranges


def trace_var(pointer, var: lldb.SBValue, pointee_type: lldb.SBType = None, allow_padding=False):
    """
    If var is not a struct or array, then return it.
    Otherwise, look through all members of var and go inside at which pointer points.
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


def get_thread_for_pointer(pointer, threads, ranges):
    left = -1
    right = len(threads) - 1
    while right - left > 1:
        middle = (left + right) // 2
        if pointer <= ranges[middle][1]:
            right = middle
        else:
            left = middle
    return threads[right] if ranges[right][0] <= pointer <= ranges[right][1] else None


def get_frame_for_pointer(pointer, thread: lldb.SBThread):
    """
    Find the frame that contains pointer or None.
    It works on the assumption that thread.GetFrames() returns frames in increasing CanonicalFrameAddress order
    """
    left = -1
    right = thread.GetNumFrames() - 1
    while right - left > 1:
        middle = (left + right) // 2
        if pointer < thread.GetFrameAtIndex(middle).GetCFA():
            right = middle
        else:
            left = middle
    return thread.GetFrameAtIndex(right) if pointer < thread.GetFrameAtIndex(right).GetCFA() else None


@log_time
def trace_pointer(pointer, process: lldb.SBProcess, pointee_type: lldb.SBType = None):
    """
    Finding thread, stack, function, object to which the pointer points
    """
    if pointee_type and pointee_type.name == 'void':
        pointee_type = None
    thread = get_thread_for_pointer(pointer, *get_threads_with_ranges(process))
    if thread:
        frame = get_frame_for_pointer(pointer, thread)
        if frame:
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
    """
    Code below runs with 'command script import script.py'
    """
    debugger.HandleCommand('command script add -f script.visualise_pointers vp')
    debugger.HandleCommand('command script add -f script.tp tp')
