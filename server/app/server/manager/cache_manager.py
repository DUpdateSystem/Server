from app.database.cache_api import get_release_cache, add_release_cache, get_memory_cache, add_memory_cache
from app.database.init import connect_db, close_db


class CacheManager:

    def __init__(self):
        self.__redis_client = None

    @staticmethod
    def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: list):
        connect_db()
        add_release_cache(hub_uuid, auth, app_id, release)
        close_db()

    @staticmethod
    def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
        connect_db()
        value = get_release_cache(hub_uuid, auth, app_id)
        close_db()
        return value

    @staticmethod
    def add_tmp_cache(key, value: str):
        connect_db()
        add_memory_cache(key, value)
        close_db()

    @staticmethod
    def get_tmp_cache(key) -> str or None:
        connect_db()
        value = get_memory_cache(key)
        close_db()
        return value


cache_manager = CacheManager()
