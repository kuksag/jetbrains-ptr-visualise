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
        # Inspect only last TESTS runs
        run = 1
        for line in reversed(log.readlines()):
            if 'script_started' in line:
                run += 1
                if run == TESTS:
                    break
            if 'trace_pointer' not in line and 'visualise_pointers' not in line:
                continue
            func, duration = line.split(':')[2].split()
            times[func].append(float(duration))
    return times


if __name__ == '__main__':
    build()
    for test in range(TESTS):
        run_debugger.run()
    logging.info('benchmark_started %s', datetime.now())
    logging.info('benchmark_runs %s', TESTS)
    for func, durations in inspect_log().items():
        logging.info(f'mean_time_{func} {sum(durations) / len(durations)}')
