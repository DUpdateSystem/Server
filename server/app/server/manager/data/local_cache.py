import functools
import time


class LocalCache:
    def __init__(self):
        self.cache_dict = {}

    def get(self, key: str) -> object or None:
        if key in self.cache_dict:
            value, time_s = self.cache_dict[key]
            if time.time() - time_s < 30 * 60:
                return value

    def add(self, key: str, value):
        self.cache_dict[key] = (value, time.time())


local_cache = LocalCache()
