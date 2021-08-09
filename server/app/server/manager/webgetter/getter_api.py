from .getter import web_getter_manager
from .getter_request_list import getter_request_list


def send_getter_request(hub_uuid: str, auth: dict or None, app_id: dict, callback, use_cache: bool = True):
    web_getter_manager.send_request(hub_uuid, auth, app_id, callback, use_cache)


def is_processing(hub_uuid: str, auth: dict, app_id: dict, use_cache: bool = True) -> int or None:
    return getter_request_list.is_processing(hub_uuid, auth, app_id, use_cache)
