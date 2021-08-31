from json import loads, dumps
from multiprocessing import Event

from app.server.utils.utils import get_manager_dict
from .callback_map import add_callback, call_callback


class RequestList:
    wait_event = Event()
    request_dict = get_manager_dict()
    processing_request_dict = get_manager_dict()

    def __popitem(self):
        while True:
            try:
                item = self.request_dict.popitem()
                return item
            except KeyError:
                self.wait_event.clear()

    def pop_request_list(self) -> tuple[str, dict, bool, list[dict]] or None:
        key, app_id_list = self.__popitem()
        try:
            processing_list = self.processing_request_dict[key]
        except KeyError:
            processing_list = []
        processing_list.append(app_id_list)
        self.processing_request_dict[key] = processing_list
        hub_uuid, auth, use_cache = self.__get_info(key)
        return hub_uuid, auth, use_cache, app_id_list.copy()

    def add_request(self, hub_uuid: str, auth: dict, app_id: dict, callback, use_cache: bool = True):
        self.__add_request(hub_uuid, auth, app_id, use_cache)
        add_callback(f'{hub_uuid}{auth}{app_id}', callback)
        self.wait_event.set()

    def callback_request(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool, *args):
        self.__pop_processing_list(hub_uuid, auth, app_id, use_cache)
        call_callback(f'{hub_uuid}{auth}{app_id}', *args)

    def is_processing(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool = True) -> bool:
        key = self.__get_key(hub_uuid, auth, use_cache)
        try:
            processing_list = self.processing_request_dict[key]
            return app_id in processing_list
        except KeyError:
            return False

    def __pop_processing_list(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool):
        key = self.__get_key(hub_uuid, auth, use_cache)
        processing_list = self.processing_request_dict[key]
        try:
            processing_list.remove(app_id)
        except ValueError:
            pass
        if not processing_list:
            del self.processing_request_dict[key]
        else:
            self.processing_request_dict[key] = processing_list

    def __add_request(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool):
        try:
            request_app_list = self.request_dict[self.__get_key(hub_uuid, auth)]
        except KeyError:
            request_app_list = []
        request_app_list.append(app_id)
        self.request_dict[self.__get_key(hub_uuid, auth, use_cache)] = request_app_list

    def is_empty(self) -> bool:
        return not self.request_dict

    @staticmethod
    def __get_key(hub_uuid: str, auth: dict, use_cache: bool = True):
        return dumps([hub_uuid, auth, use_cache], sort_keys=True, separators=(',', ':'))

    @staticmethod
    def __get_info(key_json_str: str) -> tuple[str, dict, bool]:
        key_json = loads(key_json_str)
        return key_json[0], key_json[1], key_json[2]


request_list = RequestList()
