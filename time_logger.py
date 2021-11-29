import datetime
from functools import wraps
import logging
import datetime

logging.basicConfig(filename='execution_time.log', level=logging.DEBUG, filemode='a')
logging.info('script_started: %s', datetime.datetime.now())


def log_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.datetime.now()
        result = func(*args, **kwargs)
        end = datetime.datetime.now()
        logging.info('%s %s', func.__name__, (end - start).microseconds / 10 ** 6)
        return result

    return wrapper
