import asyncio
import json
from multiprocessing import Event

import schedule

from app.server.config import server_config as _server_config
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging
from app.server.request_processor.getter_api import send_getter_request, is_processing
from app.server.utils.queue import ThreadQueue
from app.server.utils.utils import test_reliability, get_manager_list


class DataManager:

    @staticmethod
    def get_reliability_hub_dict() -> dict:
        key = "reliability_hub_dict"
        cache = cache_manager.get_tmp_cache(key)
        if cache:
            return json.loads(cache)
        reliability_hub_dict = {}
        for hub in hub_dict.values():
            test_time = test_reliability(lambda: hub.available_test())
            if test_time >= 0:
                reliability_hub_dict[hub.get_uuid()] = test_time
        cache_manager.add_tmp_cache(key, json.dumps(reliability_hub_dict))
        return reliability_hub_dict

    @staticmethod
    def init_account(hub_uuid: str, account: dict) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            raise KeyError
        hub = hub_dict[hub_uuid]
        # noinspection PyBroadException
        try:
            return hub.init_account(account)
        except Exception:
            logging.error(f"""hub_uuid: {hub_uuid} \nERROR: """, exc_info=_server_config.debug_mode)
            return None

    @staticmethod
    def get_release(hub_uuid: str, auth: dict or None, app_id: dict, use_cache: bool = True) -> list or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            raise KeyError
        event = Event()
        release_list = get_manager_list()

        def callback(_release_list=None):
            nonlocal release_list
            release_list += _release_list
            event.set()

        send_getter_request(hub_uuid, auth, app_id, callback=callback, use_cache=use_cache)
        if not event.wait(timeout=_server_config.network_timeout):
            process_time = is_processing(hub_uuid, auth, app_id, use_cache)
            if process_time:
                raise WaitingDataError(process_time)
        return list(release_list)

    def get_download_info_list(self, hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            raise KeyError
        # noinspection PyBroadException
        try:
            cache = ThreadQueue()
            asyncio.run(self.__run_download_core(hub_uuid, auth, app_id, asset_index, cache))
            download_info = next(cache)
            if type(download_info) is str:
                return [{"url": download_info}]
            else:
                return download_info
        except Exception as e:
            logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=_server_config.debug_mode)
            return e

    @staticmethod
    async def __run_download_core(hub_uuid: str, auth: dict, app_id: list, asset_index: list,
                                  generator_cache: ThreadQueue):
        hub = hub_dict[hub_uuid]
        aw = None
        download_info = None
        try:
            # noinspection PyProtectedMember
            aw = hub._get_download_info(app_id, asset_index, auth)
            download_info = await asyncio.wait_for(aw, timeout=20)
        except asyncio.TimeoutError:
            logging.info(f'aw: {aw} timeout!')
        generator_cache.put(download_info)
        generator_cache.close()

    def refresh_cache(self, uuid: str or None = None):
        i = 0
        logging.info("refresh all data: start")
        # TODO: empty
        logging.info(f"refresh all data: finish({i})")


data_manager = DataManager()


class WaitingDataError(TimeoutError):
    def __init__(self, process_time: int):
        self.process_time = process_time

    pass


def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")


schedule.every(_server_config.auto_refresh_time).hours.do(_auto_refresh)
