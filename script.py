#!/usr/bin/env python

import lldb

PATH_TO_MAPS = '/proc/{}/maps'
OUTPUT_PATTERN = '"{ptr_name}" points to object "{obj_name}", that located in "{func_name}", frame #{frame_id}, ' \
                 'of thread #{thread_id} '


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


def trace_pointer(pointer, process: lldb.SBProcess):
    """
    Finding thread, stack, function, object to which the pointer points

    :param pointer: pointer (that may be invalid) to object
    :param process: current process running
    :return: dict of info or None if pointer is invalid
    """
    for thread, (left, right) in get_threads_with_range(process):
        for frame in thread.frames:
            for var in frame.vars:
                location = read_location(var.location)
                if not location:
                    continue
                if var.type.IsArrayType() and location <= pointer <= location + var.size:
                    return {
                        'thread': thread,
                        'frame': frame,
                        'value': var,
                        'array_pos': (pointer - location) // var.type.GetArrayElementType().size
                    }
                elif location == pointer:
                    return {
                        'thread': thread,
                        'frame': frame,
                        'value': var,
                    }
    return None


def visualise_pointer(debugger, command, exe_ctx, result, internal_dict):
    pointers = list(filter(lambda x: x.type.is_pointer, exe_ctx.GetFrame().vars))
    pointers = list(map(lambda x: (x.data.uint64.all()[0], x.GetName()), pointers))
    pointers = sorted(pointers, key=lambda x: x[0])
    for pointer, ptr_name in pointers:
        info = trace_pointer(pointer, exe_ctx.GetProcess())
        if not info:
            continue
        obj_name = info['value'].GetName()
        if 'array_pos' in info:
            obj_name += f"[{info['array_pos']}]"
        print(OUTPUT_PATTERN.format(ptr_name=ptr_name,
                                    obj_name=obj_name,
                                    func_name=info['frame'].name,
                                    frame_id=info['frame'].idx,
                                    thread_id=info['thread'].idx), file=result)


def __lldb_init_module(debugger, internal_dict):
    # command script import python_code/script.py
    debugger.HandleCommand('command script add -f script.visualise_pointer vp')
