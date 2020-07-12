import asyncio
from datetime import timedelta

from requests import HTTPError
from timeloop import Timeloop

from app.config import server_config
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.hub_server_manager import HubServerManager
from app.server.utils import logging, set_new_asyncio_loop, call_def_in_loop_return_result, get_manager_list


class DataManager:
    __loop = set_new_asyncio_loop()

    def __init__(self):
        self.__hub_server_manager = HubServerManager()

    def get_response_list(self, hub_uuid: str, app_id_list: list) -> list:
        response_list = get_manager_list()
        call_def_in_loop_return_result(
            self.__get_response_package(hub_uuid, app_id_list, response_list)
            , self.__loop
        )
        return list(response_list)

    async def __get_response_package(self, hub_uuid: str, app_id_list: list, return_list: list):
        await asyncio.gather(
            *[self.___async_get_response_package(hub_uuid, app_id, return_list) for app_id in app_id_list]
        )

    async def ___async_get_response_package(self, hub_uuid: str, app_id: list, return_list: list):
        return_list.append(
            {
                "app_id": app_id,
                "app_status": self.get_app_status(hub_uuid, app_id)
            }
        )

    def get_app_status(self, hub_uuid: str, app_id: list, use_cache=True, cache_data=True) -> dict:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return {"valid_hub_uuid": False}
        return_list = self.__get_release_info(hub_uuid, app_id, use_cache=use_cache, cache_data=cache_data)
        valid_app = False
        if return_list:
            valid_app = True
        return {
            "valid_hub_uuid": True,
            "valid_app": valid_app,
            "release_info": return_list
        }

    def get_download_info(self, hub_uuid: str, app_id: list, asset_index: list) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = self.__hub_server_manager.get_hub(hub_uuid)
        # noinspection PyBroadException
        try:
            return hub.get_download_info(app_id, asset_index)
        except Exception:
            logging.error(f"""app_info: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    def refresh_cache(self):
        i = 0
        logging.info("refresh all data: start")
        cache_queue = cache_manager.cached_app_queue
        for hub_uuid in cache_queue.keys():
            for app_info in cache_queue[hub_uuid]:
                i += 1
                self.__get_release_info(hub_uuid, app_info, use_cache=False)
        logging.info(f"refresh all data: finish({i})")

    def __get_release_info(self, hub_uuid: str, app_id: list, use_cache=True, cache_data=True) -> list or None:
        if use_cache:
            # 尝试取缓存
            try:
                return cache_manager.get_release_cache(hub_uuid, app_id)
            except (KeyError, NameError):
                pass

        # 获取云端数据
        data_valid = False
        release_info = None
        # noinspection PyBroadException
        try:
            hub = self.__hub_server_manager.get_hub(hub_uuid)
            release_info = hub.get_release_info(app_id)
            data_valid = True
        except HTTPError as e:
            status_code = e.response.status_code
            if status_code == 404:
                logging.warning(f"""app_info: {app_id}
HTTP CODE 404 ERROR: {e}""")
                data_valid = True
        except Exception:
            logging.error(f"""app_info: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
        # 缓存数据，包括 404 None 数据
        if cache_data and data_valid:
            cache_manager.add_release_cache(hub_uuid, app_id, release_info)
        return release_info


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")
