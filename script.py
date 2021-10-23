#!/usr/bin/env python

import lldb

PATH_TO_MAPS = '/proc/{}/maps'


def get_range(pid, pointer):
    with open(PATH_TO_MAPS.format(pid), 'r') as maps:
        for line in maps:
            # parse '0x12-0x34 56 78' to (0x12, 0x34) and cast to base 10
            left, right = list(map(lambda x: int(x, 16), line.split()[0].split('-')))
            if left <= pointer <= right:
                return left, right


def visualise_pointer(debugger, command, exe_ctx, result, internal_dict):
    if len(command.split()) != 1:
        print('Expected exactly one argument (name of the pointer)', file=result)
        return
    pointer_value = exe_ctx.GetFrame().FindVariable(command).data.uint64.all()[0]
    pid = exe_ctx.GetProcess().id
    for thread in exe_ctx.GetProcess():
        left, right = get_range(pid, thread.frames[0].sp) or (None, None)
        if (left or right) is None:
            print("Can't find range for thread #{} in {}".format(thread.idx, PATH_TO_MAPS.format(pid)), file=result)
        elif left <= pointer_value <= right:
            for frame in thread.frames:
                for var in frame.vars:
                    try:
                        location = int(var.location, 16)
                        if location == pointer_value:
                            print('Found {} in thread #{}, frame #{}'.format(pointer_value, thread.idx, frame.idx),
                                  file=result)
                    except Exception:
                        pass


def __lldb_init_module(debugger, internal_dict):
    # command script import python_code/script.py
    debugger.HandleCommand('command script add -f script.visualise_pointer vp')
    print('Script injected.')
