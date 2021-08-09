import asyncio
from threading import Thread

from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging
from app.server.manager.data.generator_cache import GeneratorCache
from app.status_checker.status import set_hub_available, get_hub_available


def get_release(hub_uuid: str, app_id_list: list, auth: dict or None,
                use_cache=True, cache_data=True, stop_core=None):
    from app.server.hubs.hub_list import hub_dict
    hub = hub_dict[hub_uuid]
    response_queue = GeneratorCache()
    if use_cache:
        release_list_iter, thread = _get_release_cache(hub_uuid, app_id_list, response_queue, close_queue=True)
        for app_id, release_list in release_list_iter:
            if release_list is not None and not (len(release_list) == 1 and release_list[0] is None):
                yield app_id, release_list
                app_id_list.remove(app_id)
        thread.join()
    if app_id_list:
        release_list_iter, thread = _get_release_nocache(hub, app_id_list, auth, response_queue, close_queue=True)
        for item in release_list_iter:
            app_id = item["id"]
            release_list = item["v"]
            yield app_id, release_list
            app_id_list.remove(app_id)
            if cache_data:
                if release_list is not None:
                    cache_manager.add_release_cache(hub_uuid, app_id, release_list)
        thread.join()
    if stop_core:
        stop_core()


def __check_response_queue(response_queue: GeneratorCache or None) -> tuple[GeneratorCache, bool]:
    if response_queue is None:
        response_queue = GeneratorCache()
        close_queue = True
    else:
        close_queue = False
    return response_queue, close_queue


def _get_release_cache(hub_uuid: str, app_id_list: list,
                       response_queue: GeneratorCache or None, close_queue: bool = None) -> tuple:
    if close_queue is None or response_queue is None:
        response_queue, close_queue = __check_response_queue(response_queue)
    thread = Thread(target=asyncio.run,
                    args=(__get_release_cache_async(hub_uuid, app_id_list, response_queue, close_queue),))
    thread.start()
    return response_queue, thread


async def __get_release_cache_async(hub_uuid: str, app_id_list: list,
                                    response_queue: GeneratorCache, close_queue: bool):
    core_list = [__get_release_cache_async_container(response_queue, hub_uuid, app_id)
                 for app_id in app_id_list]
    await asyncio.gather(*core_list)
    if close_queue:
        response_queue.close()


async def __get_release_cache_async_container(generator_cache: GeneratorCache, hub_uuid: str, app_id: dict):
    try:
        await __run_core(__get_release_cache(generator_cache, hub_uuid, app_id), 1, True)
    except asyncio.TimeoutError:
        logging.info(f'get_release_cache: {app_id} timeout!')


async def __get_release_cache(generator_cache: GeneratorCache, hub_uuid: str, app_id: dict) -> dict or None:
    try:
        release_cache = cache_manager.get_release_cache(hub_uuid, app_id)
        generator_cache.add_value((app_id, release_cache))
    except (KeyError, NameError):
        pass


def _get_release_nocache(hub, app_id_list: list, auth: dict or None,
                         response_queue: GeneratorCache or None, close_queue: bool = None) -> tuple:
    if close_queue is None or response_queue is None:
        response_queue, close_queue = __check_response_queue(response_queue)
    thread = Thread(target=asyncio.run,
                    args=(__run_get_release_fun(hub, app_id_list, auth, response_queue, close_queue),))
    thread.start()
    return response_queue, thread


async def __run_get_release_fun(hub, app_id_list: list, auth: dict or None,
                                generator_cache: GeneratorCache, close_queue: bool):
    hub_uuid = hub.get_uuid()
    # noinspection PyBroadException
    try:
        if get_hub_available(hub_uuid):
            hub_core = hub.get_release_list(generator_cache, app_id_list, auth)
            await __run_core(hub_core, len(app_id_list))
        set_hub_available(hub_uuid, True)
    except Exception:
        set_hub_available(hub_uuid, False)
    finally:
        if close_queue:
            generator_cache.close()


async def __run_core(aw, item_num: int, raise_error: bool = False):
    timeout = item_num * 15
    if timeout > 120:
        timeout = 120
    try:
        await asyncio.wait_for(aw, timeout=timeout)
    except asyncio.TimeoutError:
        if raise_error:
            raise asyncio.TimeoutError
        else:
            logging.info(f'aw: {aw} timeout!')
