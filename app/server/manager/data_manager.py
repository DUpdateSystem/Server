import json
from datetime import timedelta
from urllib.parse import urlparse

from app.server.config import server_config
from app.server.hubs.hub_list import hub_dict, hub_url_dict
from app.server.manager.cache_manager import cache_manager
from app.server.utils import logging, time_loop


class DataManager:

    @staticmethod
    def init_account(hub_uuid: str, account: dict) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
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

    @staticmethod
    def get_download_info(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
        # noinspection PyBroadException
        try:
            return hub.get_download_info(app_id, asset_index, auth)
        except Exception:
            logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    @staticmethod
    def download_file(url: str, auth: dict) -> dict or None:
        o = urlparse(url)
        if o != 'grcp':
            logging.warning(f"UNSUPPORTED PROTOCOL: {url}")
            return None
        path_list = [path for path in o.path.split('/') if path]
        hub_url = path_list[0]
        if hub_url not in hub_url_dict:
            logging.warning(f"NO HUB: {hub_url}")
            return None
        hub = hub_url_dict[hub_url]
        # noinspection PyBroadException
        try:
            return hub.download(path_list[1:], auth)
        except Exception:
            logging.error(f"""url: {url} \nERROR: """, exc_info=server_config.debug_mode)
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
                cache_data[json.dumps(app_id)] = release_list
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
        hub = hub_dict[hub_uuid]
        nocache_data = hub.get_release_list(nocache, auth)
        if nocache_data:
            data = {**data, **nocache_data}
            if cache_data:
                for app_id in nocache_data:
                    cache_manager.add_release_cache(hub_uuid, json.loads(app_id), data[app_id])
        return data


data_manager = DataManager()


@time_loop.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")
