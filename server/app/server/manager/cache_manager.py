from app.database.cache_api import get_release_cache, add_release_cache, get_memory_cache, add_memory_cache
from app.database.init import connect_db, close_db


class CacheManager:

    def __init__(self):
        self.__redis_client = None

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
    def add_tmp_cache(key, value: str):
        add_memory_cache(key, value)

    @staticmethod
    def get_tmp_cache(key) -> str or None:
        value = get_memory_cache(key)
        return value


cache_manager = CacheManager()
