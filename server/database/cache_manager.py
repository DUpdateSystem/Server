from .cache_api import get_release_cache, add_release_cache, get_memory_cache, add_memory_cache, del_memory_cache
from .init import connect_db, close_db, init_database
from .meta import memory_db, local_cache_db
from .utils.db_wapper import db_fun


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
    @db_fun
    def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: list):
        add_release_cache(hub_uuid, auth, app_id, release)

    @staticmethod
    @db_fun
    def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
        return get_release_cache(hub_uuid, auth, app_id)

    @staticmethod
    @db_fun(memory_db)
    def add_tmp_cache(key, value: bytes):
        add_memory_cache(key, value)

    @staticmethod
    @db_fun(memory_db)
    def get_tmp_cache(key) -> bytes or None:
        value = get_memory_cache(key)
        return value

    @staticmethod
    @db_fun(memory_db)
    def del_tmp_cache(key):
        del_memory_cache(key)


cache_manager = CacheManager()
