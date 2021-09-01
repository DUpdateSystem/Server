import asyncio
import time
from multiprocessing import Manager
from threading import Thread

import schedule
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


def call_def_in_loop_return_result(core, _loop=None):
    if _loop:
        loop = _loop
    else:
        loop = set_new_asyncio_loop()
    try:
        result = loop.run_until_complete(core)
    except RuntimeError:
        future = asyncio.run_coroutine_threadsafe(core, loop)
        result = future.result()
    if not _loop:
        loop.close()
    return result


def call_fun_in_loop(core, loop):
    try:
        loop.run_until_complete(core)
    except RuntimeError:
        asyncio.run_coroutine_threadsafe(core, loop)


def call_fun_list_in_loop(core_list: list, loop=set_new_asyncio_loop()) -> tuple:
    return call_def_in_loop_return_result(__call_fun_list_in_loop(core_list), loop)


def call_fun_list_asyncio_no_return(core_list: list):
    asyncio.run(__call_fun_list_in_loop(core_list), debug=server_config.debug_mode)


async def __call_fun_list_in_loop(core_list: list) -> tuple:
    return await asyncio.gather(*core_list)


async def call_async_fun_with_id(core_id, core) -> tuple:
    return core_id, core()


__manager = Manager()


def get_manager_lock():
    return __manager.Lock()


def get_manager_value(key, value):
    return __manager.Value(key, value)


def get_manager_list():
    return __manager.list()


def get_manager_dict():
    return __manager.dict()


def hash_dict_list(func):
    class HDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    def wrapper(*args, **kwargs):
        print(args)
        args = [tuple(arg) if type(arg) == list else HDict(arg) if isinstance(arg, dict) else arg for arg in args]
        kwargs = {k: HDict(v) if isinstance(v, dict) else v for k, v in kwargs.items()}
        return func(*args, **kwargs)

    return wrapper


def __start_schedule():
    while True:
        schedule.run_pending()
        time.sleep(15 * 60)


def start_schedule():
    Thread(target=__start_schedule).start()


def test_reliability(core) -> int:
    """可靠性测试，重复调用 core 并计算平均时间
    Returns: int
      如果 core 返回非空值，返回平均执行时间（取整）
      否则，返回 -1
    """
    test_num = 3
    start = time.perf_counter()
    for _ in range(test_num):
        if not core():
            return -1
    end = time.perf_counter()
    return int((start - end) / test_num)
