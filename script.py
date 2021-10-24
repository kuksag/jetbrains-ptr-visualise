#!/usr/bin/env python

import lldb

PATH_TO_MAPS = '/proc/{}/maps'


def get_threads_with_range(process: lldb.SBProcess):
    threads = sorted(process.threads, key=lambda x: x.frames[0].sp)
    ranges = []
    ptr = 0
    with open(PATH_TO_MAPS.format(process.id), 'r') as maps:
        for line in maps:
            # parse '0x12-0x34 56 78' to (0x12, 0x34) and cast to base 10
            left, right = list(map(lambda x: int(x, 16), line.split()[0].split('-')))
            if ptr < len(threads) and left <= threads[ptr].frames[0].sp <= right:
                ranges.append((left, right))
                ptr += 1
    return list(zip(threads, ranges))


def visualise_pointer(debugger, command, exe_ctx, result, internal_dict):
    if len(command.split()) != 1:
        print('Expected exactly one argument (name of the pointer)', file=result)
        return
    pointer_value = exe_ctx.GetFrame().FindVariable(command).data.uint64.all()[0]
    for thread, (left, right) in get_threads_with_range(exe_ctx.GetProcess()):
        if left <= pointer_value <= right:
            for frame in thread.frames:
                for var in frame.vars:
                    try:
                        location = int(var.location, 16)
                        if location == pointer_value:
                            print('Found {} in thread #{}, frame #{}'.format(pointer_value, thread.idx, frame.idx),
                                  file=result)
                            return
                    except Exception:
                        # suppress failed int-16 cast
                        pass


def __lldb_init_module(debugger, internal_dict):
    # command script import python_code/script.py
    debugger.HandleCommand('command script add -f script.visualise_pointer vp')
    print('Script injected.')
