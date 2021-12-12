from database.cache_manager import cache_manager
from getter.net_getter.hub_checker import check_hub_available
from utils.logging import logging
from config import debug_mode


def get_single_release(hub_uuid: str, auth: dict or None, app_id: dict,
                       use_cache=True, cache_data=True) -> list or None:
    try:
        return next(get_release_list(hub_uuid, auth, [app_id], use_cache=use_cache, cache_data=cache_data))[4]
    except Exception as e:
        logging.exception(e)


def get_release_list(hub_uuid: str, auth: dict or None, app_id_list: list,
                     use_cache=True, cache_data=True) -> list or None:
    from getter.hubs.hub_list import hub_dict
    hub = hub_dict[hub_uuid]
    if use_cache and not debug_mode:
        for app_id in app_id_list:
            cache = __get_release_cache(hub_uuid, auth, app_id)
            if cache is not None:
                yield hub_uuid, auth, app_id, use_cache, cache
                app_id_list.remove(app_id)
    if app_id_list:
        if not check_hub_available(hub):
            return None
        for app_id, release_list in hub.get_release_list(app_id_list, auth):
            if cache_data:
                if release_list is not None:
                    cache_manager.add_release_cache(hub_uuid, auth, app_id, release_list)
            yield hub_uuid, auth, app_id, use_cache, release_list


def __get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> dict or None:
    try:
        return cache_manager.get_release_cache(hub_uuid, auth, app_id)
    except (KeyError, NameError):
        pass
