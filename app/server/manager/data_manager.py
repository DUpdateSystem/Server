import asyncio
from datetime import timedelta

from requests import HTTPError
from timeloop import Timeloop

from app.config import logging
from app.config import server_config
from app.grpc_server.route_pb2 import AppStatus, ResponsePackage, RequestList
from app.server.hubs.library.hub_list import hub_dict
from app.server.manager.cache_manager import CacheManager
from app.server.manager.hub_server_manager import HubServerManager
from app.server.utils import str_repeated_composite_container

debug_mode = False


class DataManager:

    def __init__(self):
        self.__cache_manager = CacheManager()
        self.__hub_server_manager = HubServerManager()

    def get_response_list(self, hub_uuid: str, app_id_list: list) -> RequestList:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response_list = loop.run_until_complete(
            asyncio.gather(
                *[self.__get_response_package(hub_uuid, app_id) for app_id in app_id_list]
            ))
        loop.close()
        return response_list

    async def __get_response_package(self, hub_uuid: str, app_id: list) -> ResponsePackage:
        return ResponsePackage(
            app_id=app_id,
            app_status=self.get_app_status(hub_uuid, app_id)
        )

    def get_app_status(self, hub_uuid: str, app_id: list) -> AppStatus:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return AppStatus(valid_hub_uuid=False)
        return_list = self.__get_release_info(hub_uuid, app_id)
        valid_app = False
        if return_list:
            valid_app = True
        return AppStatus(valid_hub_uuid=True, valid_app=valid_app, release_info=return_list)

    def refresh_cache(self):
        cache_queue = self.__cache_manager.cache_queue
        for hub_uuid in cache_queue.keys():
            for app_info in cache_queue[hub_uuid]:
                self.__get_release_info(hub_uuid, app_info, use_cache=False)

    def __get_release_info(self, hub_uuid: str, app_info: list, use_cache=True) -> list or None:
        if use_cache:
            # 尝试取缓存
            try:
                return self.__cache_manager.get_cache(hub_uuid, app_info)
            except KeyError or NameError:
                pass

        # 获取云端数据
        cache_data = False
        release_info = None
        try:
            hub = self.__hub_server_manager.get_hub(hub_uuid)
            release_info = hub.get_release_info(app_info)
            cache_data = True
        except HTTPError as e:
            status_code = e.response.status_code
            if status_code == 404:
                logging.warning(f"""app_info: {str_repeated_composite_container(app_info)}
HTTP CODE 404 ERROR: {e}""")
                cache_data = True
        except Exception as e:
            logging.error(f"""app_info: {str_repeated_composite_container(app_info)}
ERROR: {e}""")
            if debug_mode:
                raise e
        # 缓存数据，包括 404 None 数据
        if cache_data:
            self.__cache_manager.add_to_cache_queue(hub_uuid, app_info, release_info)
        return release_info


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")


tl.start()
