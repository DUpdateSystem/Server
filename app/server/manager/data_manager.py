import asyncio
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

    def get_release_info_list(self, hub_uuid: str, app_info_list: list) -> list:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            asyncio.gather(
                *[self.__get_release_info(hub_uuid, app_info) for app_info in app_info_list]
            ))
        loop.close()
        return_list = []
        for release_info_dict in results:
            return_list.append({
                "app_info": release_info_dict.get("app_info"),
                "release_info": release_info_dict.get("release_info")
            })
        return return_list

    @staticmethod
    async def __get_release_info(hub_uuid: str, app_info: list) -> dict:
        try:
            release_info = data_manager.get_release_info(hub_uuid, app_info)
            return {
                "app_info": app_info,
                "release_info": release_info
            }
        except Exception as e:
            print(f"""
                    ERROR: {e}
                    app_info: {app_info}
                    """)
            if debug_mode:
                raise e
            return {
                "app_info": app_info,
                "release_info": None
            }

    def get_release_info(self, hub_uuid: str, app_info: list) -> list:
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
            hub = self.__hub_server_manager.get_hub(hub_uuid)
            for app_info in cache_queue[hub_uuid]:
                try:
                    release_info = hub.get_release_info(app_info)
                    self.__cache_manager.add_to_cache_queue(hub_uuid, app_info, release_info)
                except RequestException as e:
                    print(f"NETWORK ERROR: {e}")
                    pass


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    print("auto refresh data")
    data_manager.refresh_data()


tl.start()
