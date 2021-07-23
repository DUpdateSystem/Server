import asyncio

import schedule

from app.server.config import server_config as _server_config
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging
from app.server.manager.webgetter.getter_api import send_getter_request
from .data.generator_cache import GeneratorCache


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
            logging.error(f"""hub_uuid: {hub_uuid} \nERROR: """, exc_info=_server_config.debug_mode)
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

    def get_download_info_list(self, hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
        # noinspection PyBroadException
        try:
            cache = GeneratorCache()
            asyncio.run(self.__run_download_core(hub_uuid, auth, app_id, asset_index, cache))
            download_info = next(cache)
            if type(download_info) is str:
                return [{"url": download_info}]
            else:
                return download_info
        except Exception:
            logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=_server_config.debug_mode)
            return None

    @staticmethod
    async def __run_download_core(hub_uuid: str, auth: dict, app_id: list, asset_index: list,
                                  generator_cache: GeneratorCache):
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
        aw = None
        download_info = None
        try:
            # noinspection PyProtectedMember
            aw = hub._get_download_info(app_id, asset_index, auth)
            download_info = await asyncio.wait_for(aw, timeout=20)
        except asyncio.TimeoutError:
            logging.info(f'aw: {aw} timeout!')
        generator_cache.add_value(download_info)
        generator_cache.close()

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


data_manager = DataManager()


def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")


schedule.every(_server_config.auto_refresh_time).hours.do(_auto_refresh)
