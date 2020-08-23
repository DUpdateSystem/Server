from datetime import timedelta

from timeloop import Timeloop

from app.config import server_config
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.hub_server_manager import HubServerManager
from app.server.utils import logging


class DataManager:

    def __init__(self):
        self.__hub_server_manager = HubServerManager()

    def init_account(self, hub_uuid: str, account: dict) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = self.__hub_server_manager.get_hub(hub_uuid)
        # noinspection PyBroadException
        try:
            return hub.init_account(account)
        except Exception:
            logging.error(f"""hub_uuid: {hub_uuid} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    def get_release_dict(self, hub_uuid: str, app_id_list: list, auth: dict or None = None,
                         use_cache=True, cache_data=True) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        return self.__get_release(hub_uuid, app_id_list, auth, use_cache, cache_data)

    def get_download_info(self, hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = self.__hub_server_manager.get_hub(hub_uuid)
        # noinspection PyBroadException
        try:
            return hub.get_download_info(app_id, asset_index, auth)
        except Exception:
            logging.error(f"""app_info: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    def refresh_cache(self):
        i = 0
        logging.info("refresh all data: start")
        cache_queue = cache_manager.cached_app_queue
        for hub_uuid in cache_queue.keys():
            i += len(cache_queue)
            self.__get_release(hub_uuid, cache_queue[hub_uuid], use_cache=False)
        logging.info(f"refresh all data: finish({i})")

    @staticmethod
    def __get_release_cache(hub_uuid: str, app_id_list: list) -> tuple:
        nocache = []
        cache_data = {}
        for app_id in app_id_list:
            try:
                release_list = cache_manager.get_release_cache(hub_uuid, app_id)
                cache_data[frozenset(app_id)] = release_list
            except (KeyError, NameError):
                nocache.append(app_id)
        return nocache, cache_data

    def __get_release(self, hub_uuid: str, app_id_list: list, auth: dict or None = None,
                      use_cache=True, cache_data=True) -> dict:
        data = {}
        nocache = app_id_list
        if use_cache:
            nocache, cache_data = self.__get_release_cache(hub_uuid, app_id_list)
            data = {**data, **cache_data}
        hub = self.__hub_server_manager.get_hub(hub_uuid)
        nocache_data = hub.get_release_list(nocache, auth)
        data = {**data, **nocache_data}
        if cache_data:
            for app_id in data:
                cache_manager.add_release_cache(hub_uuid, app_id, data[app_id])
        return data


tl = Timeloop()
data_manager = DataManager()


@tl.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")
