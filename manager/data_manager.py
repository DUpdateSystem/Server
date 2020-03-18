from .hub_server_manager import HubServerManager


class DataManager:
    def __init__(self):
        self.__cache_manager = CacheManager()
        self.__hub_server_manager = HubServerManager()

    def get_release_info(self, hub_uuid: str, app_info: list) -> str:
        app_id = str(app_info)
        # 尝试获取缓存
        release_info = None
        try:
            release_info = self.__cache_manager.get_cache(hub_uuid, app_id)
            print(app_id + " is cached.")
        except KeyError:
            # 获取云端数据
            if release_info is None:
                hub = self.__hub_server_manager.get_hub(hub_uuid)
                release_info = hub.get_release_info(app_info)
                self.__cache_manager.add_to_cache_queue(hub_uuid, app_id, release_info)
        return release_info


class CacheManager:

    def __init__(self):
        self.__cache_queue = dict()

    def add_to_cache_queue(self, hub_uuid: str, app_id: str, release_info: str or None = None):
        cache_queue = self.__cache_queue
        hub_cache_queue = {}
        # 尝试获取目标软件源的缓存队列
        if hub_uuid in cache_queue:
            hub_cache_queue = cache_queue[hub_uuid]
        else:
            cache_queue[hub_uuid] = hub_cache_queue
        print("cache " + app_id + ".")
        hub_cache_queue[app_id] = release_info

    def get_cache(self, hub_uuid: str, app_id: str):
        hub_cache_queue = self.__cache_queue[hub_uuid]
        return hub_cache_queue[app_id]
