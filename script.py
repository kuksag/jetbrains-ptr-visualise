#!/usr/bin/env python

import lldb
import attr

PATH_TO_MAPS = '/proc/{}/maps'
OUTPUT_PATTERN = '"{ptr_name}" points to object "{obj_name}", that located in "{func_name}", frame #{frame_id}, ' \
                 'of thread #{thread_id} '


@attr.s
class TraceInfo:
    """
    Holds info after calling trace_var(pointer, var)
    Can build a name of the target-object
    """
    thread = attr.ib(validator=attr.validators.instance_of(lldb.SBThread))
    frame = attr.ib(validator=attr.validators.instance_of(lldb.SBFrame))
    trace = attr.ib(validator=attr.validators.instance_of(list))

    def build_name_from_trace(self):
        result = ''
        for var in self.trace:
            result += var.name
            if var.num_children > 0 and not var.type.IsArrayType() and var != self.trace[-1]:
                result += '.'
        return result


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
                ranges.append((left, right))
                id += 1
    return list(zip(threads, ranges))


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


def trace_var(pointer, var: lldb.SBValue, type: lldb.SBType = None):
    """
    If var is not a struct or array, then return it.
    Otherwise, look through all members of var and go inside at which pointer points.

    :param pointer:
    :param var: current var that we look at
    :raises ValueError:
    :return: list of lldb.SBValue
    """
    if var.num_children > 0 and not var.type.is_pointer and var.type != type:
        for child in var.children:
            location = read_location(child.location)
            if not location:
                continue
            if location <= pointer < location + child.size:
                return [var] + trace_var(pointer, child)
        raise RuntimeError(f"{pointer} not found in {var.name}")
    else:
        if read_location(var.location) != pointer:
            raise RuntimeError(f"pointer {pointer} doesnt match with found address {read_location(var.location)}")
        if type is not None and type != var.type:
            raise RuntimeError(f"pointer type {type} doesn't match with found type {var.type}")
        return [var]


def trace_pointer(pointer, process: lldb.SBProcess, type: lldb.SBType = None):
    """
    Finding thread, stack, function, object to which the pointer points

    :param pointer: pointer (that may be invalid) to object
    :param process: current process running
    :return: TraceInfo or None
    """
    for thread, (left, right) in get_threads_with_range(process):
        for frame in thread.frames:
            for var in frame.vars:
                location = read_location(var.location)
                if not location:
                    continue
                if location <= pointer < location + var.size:
                    return TraceInfo(thread, frame, trace_var(pointer, var, type))
    return None


def tp(debugger, command, exe_ctx, result, internal_dict):
    """
    Alias to call from debugger
    """
    # trace_info = trace_pointer(read_location(command), exe_ctx.GetProcess())
    trace_info = trace_pointer(int(command), exe_ctx.GetProcess())
    if trace_info:
        print(trace_info.build_name_from_trace(), file=result)
    else:
        print('not found', file=result)


def visualise_pointers(debugger, command, exe_ctx, result, internal_dict):
    """
    Take all pointers from current frame and find their target
    """
    pointers = list(filter(lambda x: x.type.is_pointer, exe_ctx.GetFrame().vars))
    pointers = list(map(lambda x: (x.data.uint64s[0], x.GetName(), x.type.GetPointeeType()), pointers))
    for pointer, ptr_name, pointee_type in pointers:
        trace_info = trace_pointer(pointer, exe_ctx.GetProcess(), pointee_type)
        if not trace_info:
            print(f'target not found for {ptr_name}', file=result)
        else:
            print(OUTPUT_PATTERN.format(ptr_name=ptr_name,
                                        obj_name=trace_info.build_name_from_trace(),
                                        func_name=trace_info.frame.name,
                                        frame_id=trace_info.frame.idx,
                                        thread_id=trace_info.thread.idx), file=result)


def __lldb_init_module(debugger, internal_dict):
    # command script import python_code/script.py
    debugger.HandleCommand('command script add -f script.visualise_pointers vp')
    debugger.HandleCommand('command script add -f script.tp tp')
