import json

import schedule

from app.server.config import server_config as _server_config
from app.server.hubs.hub_list import hub_dict
from app.server.request_processor.api import get_cloud_config, get_release_list, get_download
from app.server.utils.queue import ThreadQueue
from app.server.utils.utils import test_reliability
from .cache_manager import cache_manager
from .data.constant import logging


class DataManager:

    @staticmethod
    def get_reliability_hub_dict() -> dict:
        key = "reliability_hub_dict"
        cache_manager.connect()
        cache = cache_manager.get_tmp_cache(key)
        if cache:
            return json.loads(cache)
        reliability_hub_dict = {}
        for hub in hub_dict.values():
            test_time = test_reliability(lambda: hub.available_test())
            if test_time >= 0:
                reliability_hub_dict[hub.get_uuid()] = test_time
        cache_manager.add_tmp_cache(key, json.dumps(reliability_hub_dict))
        cache_manager.disconnect()
        return reliability_hub_dict

    @staticmethod
    def get_cloud_config_str(dev_version: bool, migrate_master: bool) -> str or None:
        queue = ThreadQueue()
        get_cloud_config(dev_version, migrate_master, lambda value: queue.put(value))
        return queue.get()

    @staticmethod
    def get_release(hub_uuid: str, auth: dict or None, app_id: dict, use_cache: bool = True) -> list or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            raise KeyError
        queue = ThreadQueue()
        get_release_list(hub_uuid, auth, app_id, use_cache, lambda value: queue.put(value))
        return queue.get()

    @staticmethod
    def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            raise KeyError
        queue = ThreadQueue()
        get_download(hub_uuid, auth, app_id, asset_index, lambda value: queue.put(value))
        return queue.get()

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
