from functools import wraps
from threading import Lock

from ..init import connect_db, close_db

db_lock = Lock()


def db_fun(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with db_lock:
            connect_db()
            value = func(*args, **kwargs)
            close_db()
            return value

    return wrapper
