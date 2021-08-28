from json import loads, dumps
from threading import Lock
from time import time

from app.server.manager.data.constant import logging
from app.server.utils.function_register import function_register


class GetterRequestList:
    request_dict = dict()
    processing_request_dict = dict()
    request_dict_lock = Lock()

    def pop_request_list(self) -> tuple[str, dict, bool, list[dict]]:
        with self.request_dict_lock:
            key, app_id_list = self.request_dict.popitem()
            self.processing_request_dict[key] = [app_id_list, time()]
            hub_uuid, auth, use_cache = self.__get_info(key)
            return hub_uuid, auth, use_cache, app_id_list.copy()

    def add_request(self, hub_uuid: str, auth: dict, app_id: dict, callback, use_cache: bool = True):
        with self.request_dict_lock:
            self.__add_request(hub_uuid, auth, app_id, use_cache)
        function_register.add_function(f'{hub_uuid}{auth}{app_id}', callback)

    def callback_request(self, hub_uuid: str, auth: dict, use_cache: bool, app_id: dict, *args):
        try:
            self.__callback_request(hub_uuid, auth, use_cache, app_id, *args)
        except Exception as e:
            logging.exception(e)

    def __callback_request(self, hub_uuid: str, auth: dict, use_cache: bool, app_id: dict, *args):
        with self.request_dict_lock:
            self.__pop_processing_list(hub_uuid, auth, use_cache, app_id)
        function_register.call_function(f'{hub_uuid}{auth}{app_id}', *args)

    def __pop_processing_list(self, hub_uuid: str, auth: dict, use_cache: bool, app_id: dict):
        key = self.__get_key(hub_uuid, auth, use_cache)
        processing_request_list: list = self.processing_request_dict[key]
        app_id_list = processing_request_list[0]
        try:
            app_id_list.remove(app_id)
        except ValueError:
            pass
        if not app_id_list:
            self.processing_request_dict.pop(key)
        else:
            processing_request_list[1] = time()

    def is_processing(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool = True) -> int or None:
        key = self.__get_key(hub_uuid, auth, use_cache)
        try:
            app_id_list, process_time = self.processing_request_dict[key]
            if app_id in app_id_list:
                return process_time
            else:
                return None
        except KeyError:
            return False

    def __add_request(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool):
        try:
            request_list = self.request_dict[self.__get_key(hub_uuid, auth)]
        except KeyError:
            request_list = []
        request_list.append(app_id)
        self.request_dict[self.__get_key(hub_uuid, auth, use_cache)] = request_list

    def is_empty(self) -> bool:
        return not self.request_dict

    @staticmethod
    def __get_key(hub_uuid: str, auth: dict, use_cache: bool = True):
        return dumps([hub_uuid, auth, use_cache], sort_keys=True, separators=(',', ':'))

    @staticmethod
    def __get_info(key_json_str: str) -> tuple[str, dict, bool]:
        key_json = loads(key_json_str)
        return key_json[0], key_json[1], key_json[2]


getter_request_list = GetterRequestList()
