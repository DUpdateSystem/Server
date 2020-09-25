import asyncio
from multiprocessing import Manager

from requests import Response

from app.server.config import server_config
from app.server.manager.data.constant import session as __session, proxies as __proxies


def get_response(url: str, throw_error=False, **kwargs) -> Response or None:
    try:
        response = __session.get(url, **kwargs, proxies=__proxies, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        if throw_error:
            raise e
        return None


def run_fun_list(core_list):
    for core in core_list:
        core()


def set_new_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if server_config.debug_mode:
        loop.set_debug(True)
    return loop


def call_def_in_loop_return_result(core, loop):
    try:
        return loop.run_until_complete(core)
    except RuntimeError:
        future = asyncio.run_coroutine_threadsafe(core, loop)
    return future.result()


def call_def_in_loop(core, loop):
    try:
        loop.run_until_complete(core)
    except RuntimeError:
        asyncio.run_coroutine_threadsafe(core, loop)


def call_fun_list_in_loop(core_list: list, loop=set_new_asyncio_loop()) -> tuple:
    return call_def_in_loop_return_result(__call_fun_list_in_loop(core_list), loop)


def call_fun_list_asyncio_no_return(core_list: list):
    asyncio.run(__call_fun_list_in_loop(core_list))


async def __call_fun_list_in_loop(core_list: list) -> tuple:
    return await asyncio.gather(*core_list)


async def call_async_fun_with_id(core_id, core) -> tuple:
    return core_id, core()


def grcp_dict_list_to_dict(grcp_dict: list or None) -> dict:
    d = {}
    if grcp_dict:
        for gd in grcp_dict:
            d[gd.k] = gd.v
    return d


def dict_to_grcp_dict_list(d: dict or None) -> list:
    g_dict = []
    if d:
        for k in d:
            g_dict.append({"k": k, "v": d[k]})
    return g_dict


__manager = Manager()


def get_manager_lock():
    return __manager.Lock()


def get_manager_value(key, value):
    return __manager.Value(key, value)


def get_manager_list():
    return __manager.list()


def get_manager_dict():
    return __manager.dict()
