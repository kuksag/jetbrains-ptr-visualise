from datetime import datetime
from functools import wraps
import logging

logging.basicConfig(filename='execution_time.log', level=logging.DEBUG, filemode='a')
logging.info('script_started %s', datetime.now())


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        end = datetime.now()
        logging.info('%s %s', func.__name__, (end - start).microseconds / 10 ** 6)
        return result

    return wrapper
