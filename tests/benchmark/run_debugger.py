import lldb
import os

PATH_TO_SCRIPT = '../../script.py'
PATH_TO_SOURCE = 'main.cpp'
BREAKPOINT_ANCHOR = 'Set a breakpoint here'
VP_CALLS_NUMBER = 0
TP_CALLS_NUMBER = 5


def find_line(file_path, substr):
    with open(file_path, 'r') as file:
        for i, line in enumerate(file.readlines()):
            if substr in line:
                # because lines in file enumerated from 1
                return i + 1
    return None


def run():
    debugger: lldb.SBDebugger = lldb.SBDebugger.Create()

    debugger.SetAsync(False)

    print('Creating a target')
    target = debugger.CreateTargetWithFileAndArch('main', lldb.LLDB_ARCH_DEFAULT)

    if target:
        main_bp = target.BreakpointCreateByLocation(PATH_TO_SOURCE, find_line(PATH_TO_SOURCE, BREAKPOINT_ANCHOR))
        process = target.LaunchSimple(None, None, os.getcwd())
        if process:
            state = process.GetState()
            if state == lldb.eStateStopped:
                debugger.HandleCommand(f'command script import {PATH_TO_SCRIPT}')

                for i in range(VP_CALLS_NUMBER):
                    debugger.HandleCommand(f'vp')
                for i in range(TP_CALLS_NUMBER):
                    debugger.HandleCommand(f'tp 0')

            if state == lldb.eStateExited:
                print('Didnt hit the breakpoint at main, program has exited...')
            else:
                print(f'Unexpected process state: {debugger.StateAsCString(state)}, killing process...')
                process.Kill()


if __name__ == '__main__':
    run()
