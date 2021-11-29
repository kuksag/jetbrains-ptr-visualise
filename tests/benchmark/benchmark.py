from datetime import datetime
import subprocess
import run_debugger
from collections import defaultdict
import logging

LOG_PATH = 'execution_time.log'
TESTS = 5


def build():
    subprocess.run(['cmake', '.'])
    subprocess.run(['make'])


def inspect_log():
    times = defaultdict(list)
    with open(LOG_PATH, 'r') as log:
        for line in reversed(log.readlines()):
            if 'script_started' in line:
                break
            if 'DEBUG' in line:
                continue
            if not any(match in line for match in ['visualise_pointers', 'trace_pointer']):
                continue
            func, duration = line.split(':')[2].split()
            times[func].append(float(duration))
    return times


if __name__ == '__main__':
    build()
    for test in range(TESTS):
        run_debugger.run()
    logging.debug('benchmark_started %s', datetime.now())
    logging.debug('benchmark_runs %s', TESTS)
    for func, durations in inspect_log().items():
        logging.debug(f'mean_time_{func} {sum(durations) / len(durations)}')
