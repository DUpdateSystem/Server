import json
from timeloop import Timeloop
from datetime import timedelta
from .hub_server_manager import HubServerManager
from .cache_manager import CacheManager


class DataManager:
    def __init__(self):
        self.__cache_manager = CacheManager()
        self.__hub_server_manager = HubServerManager()

    def get_release_info(self, hub_uuid: str, app_info: list) -> str:
        app_id = json.dumps(app_info)
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

    def refresh_data(self):
        for hub_uuid in self.__cache_manager.cache_queue.keys():
            hub = self.__hub_server_manager.get_hub(hub_uuid)
            for app_info in self.__cache_manager.cache_queue[hub_uuid]:
                try:
                    release_info = hub.get_release_info(app_info)
                    self.__cache_manager.add_to_cache_queue(hub_uuid, app_info, release_info)
                except Exception:
                    pass


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=6))
def _auto_refresh():
    print("auto refresh data")
    data_manager.refresh_data()


tl.start()
