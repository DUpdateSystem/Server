from datetime import timedelta

from requests import HTTPError, Response
from timeloop import Timeloop

from app.config import server_config
from app.server.client_proxy.ask_proxy_error import NeedClientProxy
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.hub_server_manager import HubServerManager
from app.server.utils import logging, set_new_asyncio_loop


class DataManager:
    __loop = set_new_asyncio_loop()

    def __init__(self):
        self.__hub_server_manager = HubServerManager()

    def get_app_status(self, hub_uuid: str, app_id: list, use_proxy=False,
                       fun_id: int = 0, http_response: dict = None,
                       use_cache=True, cache_data=True) -> dict:
        try:
            app_status = self.__get_app_status(hub_uuid, app_id, fun_id, http_response, use_cache, cache_data)
            return {"app_status": app_status}
        except NeedClientProxy as e:
            if not use_proxy:
                raise e
            http_request_item = e.http_request_item
            return {
                "need_proxy": True,
                "next_fun_id": fun_id + 1,
                "http_proxy_request": http_request_item.to_dict()
            }

    def __get_app_status(self, hub_uuid: str, app_id: list,
                         fun_id: int = 0, http_response: dict = None,
                         use_cache=True, cache_data=True) -> dict:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return {"valid_hub_uuid": False}
        return_list = self.__get_release_info(hub_uuid, app_id, fun_id=fun_id, http_response=http_response,
                                              use_cache=use_cache, cache_data=cache_data)
        return {
            "valid_hub_uuid": True,
            "valid_app": True,
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
                try:
                    self.__get_release_info(hub_uuid, app_info, use_cache=False)
                    i += 1
                except NeedClientProxy:
                    pass
        logging.info(f"refresh all data: finish({i})")

    def __get_release_info(self, hub_uuid: str, app_id: list,
                           fun_id: int = 0, http_response: dict = None,
                           use_cache=True, cache_data=True) -> list or None:
        if use_cache:
            # 尝试取缓存
            try:
                return cache_manager.get_release_cache(hub_uuid, app_id)
            except (KeyError, NameError):
                pass

        # 获取云端数据
        release_info = None
        # noinspection PyBroadException
        try:
            release_info = self.__call_release_info_fun(hub_uuid, app_id, fun_id, http_response)
            # 缓存数据，包括 404 None 数据
            if cache_data:
                cache_manager.add_release_cache(hub_uuid, app_id, release_info)
        except NeedClientProxy as e:
            raise e
        except Exception:
            logging.error(f"""app_info: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
        return release_info

    def __call_release_info_fun(self, hub_uuid: str, app_id: list,
                                fun_id: int = 0, http_response: dict = None) -> list or None:
        # noinspection PyBroadException
        release_info = None
        try:
            # 调用爬虫函数
            if not fun_id:
                release_info = self.__get_release_info_fun(hub_uuid, fun_id)(app_id)
            else:
                # 处理客户端代理返回数据
                status_code = http_response['status_code']
                if status_code < 200 or status_code >= 400:
                    response = Response()
                    response.status_code = status_code
                    raise HTTPError(response=response)
                release_info = self.__get_release_info_fun(hub_uuid, fun_id)(app_id, http_response['text'])
        except HTTPError as e:
            status_code = e.response.status_code
            logging.warning(f"""app_info: {app_id}
        HTTP CODE {status_code} ERROR: {e}""")
            if status_code != 404:
                raise e
        return release_info

    def __get_release_info_fun(self, hub_uuid: str, fun_id: int = 0):
        hub = self.__hub_server_manager.get_hub(hub_uuid)
        if not fun_id:
            return hub.get_release_info
        else:
            fun_name = f"get_release_info_{fun_id}"
            return getattr(hub, fun_name)


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")
