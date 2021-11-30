import lldb
import os
import cProfile
import subprocess
from datetime import datetime

PATH_TO_SCRIPT = '../../script.py'
PSTAT_FOLDER = 'pstat'
PATH_TO_SOURCE = 'main.cpp'
BREAKPOINT_ANCHOR = 'Set a breakpoint here'
VP_CALLS_NUMBER = 5
TP_CALLS_NUMBER = 5


def build():
    subprocess.run(['cmake', '.'])
    subprocess.run(['make'])


def find_line(file_path, substr):
    with open(file_path, 'r') as file:
        for i, line in enumerate(file.readlines()):
            if substr in line:
                # because lines in file enumerated from 1
                return i + 1
    return None


def run():
    pr = cProfile.Profile()

    print('Building...')
    build()

    debugger: lldb.SBDebugger = lldb.SBDebugger.Create()
    debugger.SetAsync(False)
    print('Creating a target')
    target = debugger.CreateTargetWithFileAndArch('main', lldb.LLDB_ARCH_DEFAULT)

    if target:
        main_bp = target.BreakpointCreateByLocation(PATH_TO_SOURCE, find_line(PATH_TO_SOURCE, BREAKPOINT_ANCHOR))
        print('Starting a process...')
        process = target.LaunchSimple(None, None, os.getcwd())
        if process:
            state = process.GetState()
            if state == lldb.eStateStopped:
                debugger.HandleCommand(f'command script import {PATH_TO_SCRIPT}')

                pr.enable()
                for i in range(VP_CALLS_NUMBER):
                    debugger.HandleCommand(f'vp')
                for i in range(TP_CALLS_NUMBER):
                    debugger.HandleCommand(f'tp 0')
                pr.disable()

                timestr = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
                stats_filename = f"{PSTAT_FOLDER}/benchmark-{timestr}.pstat"
                if not os.path.exists(PSTAT_FOLDER):
                    os.makedirs(PSTAT_FOLDER)
                pr.dump_stats(stats_filename)

            elif state == lldb.eStateExited:
                print('Didnt hit the breakpoint at main, program has exited...')
            else:
                print(f'Unexpected process state: {debugger.StateAsCString(state)}, killing process...')
                process.Kill()
        else:
            print('Process is not running!')
    else:
        print('Target not found! Stopping...')


if __name__ == '__main__':
    run()
