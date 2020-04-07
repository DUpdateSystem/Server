from timeloop import Timeloop
from datetime import timedelta
from requests.exceptions import RequestException
from .hub_server_manager import HubServerManager
from .cache_manager import CacheManager
from ..config import server_config

debug_mode = False


class DataManager:

    def __init__(self):
        self.__cache_manager = CacheManager()
        self.__hub_server_manager = HubServerManager()

    @staticmethod
    def get_release_info(hub_uuid: str, app_info: list, use_cache=True) -> list or None:
        try:
            return data_manager.__get_release_info(hub_uuid, app_info)
        except Exception as e:
            print(f"""
                    ERROR: {e}
                    app_info: {app_info}
                    """)
            if debug_mode:
                raise e
            return None

    def __get_release_info(self, hub_uuid: str, app_info: list, use_cache=True) -> list:
        if use_cache:
            # 尝试获取缓存
            release_info = self.__cache_manager.get_cache(hub_uuid, app_info)
            if release_info is not None:
                return release_info
        # 获取云端数据
        hub = self.__hub_server_manager.get_hub(hub_uuid)
        release_info = hub.get_release_info(app_info)
        # 缓存数据
        self.__cache_manager.add_to_cache_queue(hub_uuid, app_info, release_info)
        return release_info

    def refresh_data(self):
        cache_queue = self.__cache_manager.cache_queue
        for hub_uuid in cache_queue.keys():
            for app_info in cache_queue[hub_uuid]:
                self.get_release_info(hub_uuid, app_info, use_cache=False)


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    print("auto refresh data")
    data_manager.refresh_data()


tl.start()
