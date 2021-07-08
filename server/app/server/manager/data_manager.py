from datetime import timedelta

from app.server.config import server_config
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging, time_loop
from app.server.manager.webgetter.getter_api import send_getter_request


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

    @staticmethod
    def get_release(hub_uuid: str, app_id_list: list, auth: dict or None = None,
                    use_cache: bool = True, cache_data: bool = True) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        request_queue = send_getter_request(hub_uuid, app_id_list, auth, use_cache, cache_data)
        for app_id, release_list in request_queue:
            yield {"app_id": app_id, "release_list": release_list}

    @staticmethod
    def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
        # noinspection PyBroadException
        try:
            download_info = hub.get_download_info(app_id, asset_index, auth)
            if type(download_info) is str:
                return [{"url": download_info}]
            else:
                return download_info
        except Exception:
            logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    def refresh_cache(self, uuid: str or None = None):
        i = 0
        logging.info("refresh all data: start")
        cache_queue = cache_manager.cached_app_queue
        for hub_uuid in cache_queue.keys():
            if uuid and hub_uuid != uuid:
                continue
            release_iter = self.get_release(hub_uuid, cache_queue[hub_uuid], use_cache=False)
            if release_iter:
                for _ in release_iter:
                    i += 1
        logging.info(f"refresh all data: finish({i})")

    @staticmethod
    def __get_release_cache(hub_uuid: str, app_id: dict) -> dict or None:
        try:
            return cache_manager.get_release_cache(hub_uuid, app_id)
        except (KeyError, NameError):
            pass


data_manager = DataManager()


@time_loop.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")
