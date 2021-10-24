#!/usr/bin/env python

import lldb

PATH_TO_MAPS = '/proc/{}/maps'


def get_threads_with_range(process: lldb.SBProcess):
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


def visualise_pointer(debugger, command, exe_ctx, result, internal_dict):
    pointers = list(filter(lambda x: x.type.is_pointer, exe_ctx.GetFrame().vars))
    pointers = list(map(lambda x: x.data.uint64.all()[0], pointers))
    pointers = sorted(pointers)
    id = 0
    def condition(x): return x >= len(pointers) or pointers[x] > right
    for thread, (left, right) in get_threads_with_range(exe_ctx.GetProcess()):
        while id < len(pointers) and pointers[id] < left:
            id += 1
        if condition(id):
            continue
        for frame in thread.frames:
            if condition(id):
                break
            for var in frame.vars:
                if condition(id):
                    break
                try:
                    location = int(var.location, 16)
                    if location == pointers[id]:
                        print('Found {} in thread #{}, frame #{}'.format(pointers[id], thread.idx, frame.idx),
                              file=result)
                        id += 1
                except Exception:
                    # suppress failed int-16 cast
                    pass


def __lldb_init_module(debugger, internal_dict):
    # command script import python_code/script.py
    debugger.HandleCommand('command script add -f script.visualise_pointer vp')
    print('Script injected.')
