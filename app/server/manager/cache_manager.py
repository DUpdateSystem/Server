from multiprocessing import Manager

manager = Manager()


class CacheManager:

    def __init__(self):
        self.__cache_queue = manager.dict()

    def add_to_cache_queue(self, hub_uuid: str, app_info: list, release_info: list or None = None):
        cache_queue = self.__cache_queue
        # 尝试获取目标软件源的缓存队列
        hub_cache_queue = manager.list()
        if hub_uuid in cache_queue:
            hub_cache_queue = cache_queue[hub_uuid]
        else:
            cache_queue[hub_uuid] = hub_cache_queue
        # 尝试获取目标缓存软件
        for app_cache in hub_cache_queue:
            # 删除旧缓存
            if app_cache["app_info"] == app_info:
                hub_cache_queue.remove(app_cache)
        # 写入新缓存
        app_cache_dict = {
            "app_info": app_info,
            "release_info_cache": release_info
        }
        hub_cache_queue.append(app_cache_dict)
        # 缓存完毕
        print(f"cache {app_info}.")

    def get_cache(self, hub_uuid: str, app_info: list) -> str or None:
        if hub_uuid in self.__cache_queue:
            hub_cache_queue = self.__cache_queue[hub_uuid]
            for app_cache in hub_cache_queue:
                if app_cache["app_info"] == app_info:
                    print(str(app_info) + " is cached.")
                    return app_cache["release_info_cache"]
        return None

    @property
    def cache_queue(self) -> dict:
        cache_app_info_dict = {}
        for hub_uuid in self.__cache_queue.keys():
            app_info_list = [app_info_dict["app_info"] for app_info_dict in self.__cache_queue[hub_uuid]]
            cache_app_info_dict[hub_uuid] = app_info_list
        return cache_app_info_dict
