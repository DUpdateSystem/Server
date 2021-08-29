from app.database.cache_api import get_release_cache, add_release_cache, get_memory_cache, add_memory_cache


class CacheManager:

    def __init__(self):
        self.__redis_client = None

    @staticmethod
    def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: list):
        return add_release_cache(hub_uuid, auth, app_id, release)

    @staticmethod
    def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
        return get_release_cache(hub_uuid, auth, app_id)

    @staticmethod
    def add_tmp_cache(key, value: str):
        return add_memory_cache(key, value)

    @staticmethod
    def get_tmp_cache(key) -> str or None:
        return get_memory_cache(key)


cache_manager = CacheManager()
