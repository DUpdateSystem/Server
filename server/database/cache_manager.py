from .cache_api import (add_memory_cache, add_release_cache, del_memory_cache,
                        get_memory_cache, get_release_cache)
from .init import close_db, connect_db, init_database
from .meta import local_cache_db, memory_db


class CacheManager:

    def __init__(self):
        self.__redis_client = None

    @staticmethod
    def init():
        init_database()

    @staticmethod
    def connect():
        connect_db(memory_db)
        connect_db(local_cache_db)

    @staticmethod
    def disconnect():
        close_db(memory_db)
        close_db(local_cache_db)

    @staticmethod
    @local_cache_db.connection_context()
    def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict,
                          release: list):
        add_release_cache(hub_uuid, auth, app_id, release)

    @staticmethod
    @local_cache_db.connection_context()
    def get_release_cache(hub_uuid: str, auth: dict or None,
                          app_id: dict) -> list or None:
        return get_release_cache(hub_uuid, auth, app_id)

    @staticmethod
    @memory_db.connection_context()
    def add_tmp_cache(key, value: bytes):
        add_memory_cache(key, value)

    @staticmethod
    @memory_db.connection_context()
    def get_tmp_cache(key) -> bytes or None:
        value = get_memory_cache(key)
        return value

    @staticmethod
    @memory_db.connection_context()
    def del_tmp_cache(key):
        del_memory_cache(key)


cache_manager = CacheManager()
