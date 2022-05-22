from functools import wraps
from threading import Lock

from ..init import close_db, connect_db
from ..meta import local_cache_db

db_lock = Lock()


def db_fun(db=local_cache_db):
    def db_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with db_lock:
                connect_db(db)
                value = func(*args, **kwargs)
                close_db(db)
                return value

        return wrapper

    return db_decorator
