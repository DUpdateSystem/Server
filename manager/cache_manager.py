class CacheManager:

    def __init__(self):
        self.__cache_queue = dict()

    def add_to_cache_queue(self, hub_uuid: str, app_info: list, release_info: str or None = None):
        cache_queue = self.__cache_queue
        hub_cache_queue = []
        # 尝试获取目标软件源的缓存队列
        if hub_uuid in cache_queue:
            hub_cache_queue = cache_queue[hub_uuid]
        else:
            cache_queue[hub_uuid] = hub_cache_queue
        print(f"cache {app_info}.")
        app_cache_dict = None
        for app_cache in hub_cache_queue:
            if app_cache["app_info"] == app_info:
                app_cache_dict = app_cache
        if app_cache_dict is None:
            app_cache_dict = {"app_info": app_info}
            hub_cache_queue.append(app_cache_dict)
        app_cache_dict["release_info_cache"] = release_info

    def get_cache(self, hub_uuid: str, app_info: list) -> str:
        hub_cache_queue = self.__cache_queue[hub_uuid]
        for app_cache in hub_cache_queue:
            if app_cache["app_info"] == app_info:
                return app_cache["release_info_cache"]

    @property
    def cache_queue(self) -> dict:
        cache_app_info_dict = {}
        for hub_uuid in self.__cache_queue.keys():
            app_info_list = [app_info_dict["app_info"] for app_info_dict in self.__cache_queue[hub_uuid]]
            cache_app_info_dict[hub_uuid] = app_info_list
        return cache_app_info_dict
