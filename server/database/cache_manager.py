from utils.logging import logging
from .cache_api import get_release_cache, add_release_cache, get_memory_cache, add_memory_cache
from .init import connect_db, close_db, init_database


class CacheManager:

    def __init__(self):
        self.__redis_client = None

    @staticmethod
    def init():
        init_database()

    @staticmethod
    def connect():
        connect_db()

    @staticmethod
    def disconnect():
        close_db()

    @staticmethod
    def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: list):
        add_release_cache(hub_uuid, auth, app_id, release)

    @staticmethod
    def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
        return get_release_cache(hub_uuid, auth, app_id)

    @staticmethod
    def add_tmp_cache(key, value: bytes):
        add_memory_cache(key, value)

    @staticmethod
    def get_tmp_cache(key) -> bytes or None:
        value = get_memory_cache(key)
        return value


cache_manager = CacheManager()
