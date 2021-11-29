import os
import subprocess
import run_debugger
from collections import defaultdict

LOG_PATH = 'execution_time.log'
TESTS = 5


def build():
    subprocess.run(['cmake', '.'])
    subprocess.run(['make'])


def remove_previous_log():
    try:
        os.remove(LOG_PATH)
    except FileNotFoundError:
        pass


def inspect_log():
    times = defaultdict(list)
    with open(LOG_PATH, 'r') as log:
        for line in log:
            if 'trace_pointer' not in line and 'visualise_pointers' not in line:
                continue
            func, duration = line.split(':')[2].split()
            times[func].append(float(duration))
    return times


if __name__ == '__main__':
    remove_previous_log()
    build()
    for test in range(TESTS):
        run_debugger.run()
    for func, durations in inspect_log().items():
        print(f'{func}: {sum(durations) / len(durations)}')
