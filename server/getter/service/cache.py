from database.cache_manager import cache_manager
from utils.logging import logging


def get_tmp_cache_or_run(key, core, *args):
    def get_cache_fun():
        return cache_manager.get_tmp_cache(key).decode()

    def set_cache_fun(value):
        return cache_manager.add_tmp_cache(key, value.encode())

    return get_cache_or_run(get_cache_fun, set_cache_fun, core, *args)


def get_re_cache_or_run(hub_uuid: str, auth: dict or None, app_id: dict, fun):
    def get_cache_fun():
        return cache_manager.get_release_cache(hub_uuid, auth, app_id)

    def set_cache_fun(value):
        return cache_manager.add_release_cache(hub_uuid, auth, app_id, value)

    return get_cache_or_run(get_cache_fun, set_cache_fun, fun, hub_uuid, auth, app_id)


def get_cache_or_run(get_cache_fun, set_cache_fun, core, *core_args):
    try:
        cache_string = get_cache_fun()
    except AttributeError or KeyError:
        cache_string = None
    except Exception as e:
        cache_manager.del_tmp_cache()
        cache_string = None
        logging.info(f"缓存错误（清除）: {core} | {core_args}, error: {e}")
    if cache_string:
        return cache_string
    cache_string = core(*core_args)
    if cache_string:
        set_cache_fun(cache_string)
    return cache_string
