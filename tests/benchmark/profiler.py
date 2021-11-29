import cProfile
import run_debugger
import subprocess
from datetime import datetime


def build():
    subprocess.run(['cmake', '.'])
    subprocess.run(['make'])


if __name__ == '__main__':
    pr = cProfile.Profile()

    build()
    pr.enable()
    run_debugger.run()
    pr.disable()

    # timestr = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    timestr = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    stats_filename = f"benchmark-{timestr}.pstat"
    pr.dump_stats(stats_filename)
