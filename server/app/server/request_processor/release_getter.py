import asyncio
from threading import Thread

from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging
from app.server.utils.queue import ThreadQueue, LightQueue
from app.status_checker.status import set_hub_available, get_hub_available


async def get_release(return_queue: LightQueue, hub_uuid: str, auth: dict or None, app_id_list: list,
                      use_cache=True, cache_data=True):
    from app.server.hubs.hub_list import hub_dict
    hub = hub_dict[hub_uuid]
    observer_queue = ThreadQueue()
    if use_cache:
        thread = _get_release_cache(observer_queue, hub_uuid, auth, app_id_list)
        for app_id, release_list in observer_queue:
            await return_queue.put((hub_uuid, auth, app_id, use_cache, release_list))
            if release_list is not None and not (len(release_list) == 1 and release_list[0] is None):
                app_id_list.remove(app_id)
        thread.join()
    if app_id_list:
        thread = _get_release_nocache(observer_queue, hub, app_id_list, auth)
        for item in observer_queue:
            app_id = item["id"]
            release_list = item["v"]
            await return_queue.put((hub_uuid, auth, app_id, use_cache, release_list))
            if cache_data:
                if release_list is not None:
                    cache_manager.add_release_cache(hub_uuid, auth, app_id, release_list)
        thread.join()


def _get_release_cache(queue: ThreadQueue, hub_uuid: str, auth: dict or None, app_id_list: list) -> Thread:
    thread = Thread(target=asyncio.run, args=(__get_release_cache_async(queue, hub_uuid, auth, app_id_list),))
    thread.start()
    return thread


async def __get_release_cache_async(queue: ThreadQueue, hub_uuid: str, auth: dict or None, app_id_list: list):
    core_list = [__get_release_cache_async_container(queue, hub_uuid, auth, app_id) for app_id in app_id_list]
    await asyncio.gather(*core_list)
    queue.close()


async def __get_release_cache_async_container(queue: ThreadQueue, hub_uuid: str, auth: dict or None, app_id: dict):
    try:
        await __run_core(__get_release_cache(queue, hub_uuid, auth, app_id), 1, True)
    except asyncio.TimeoutError:
        logging.info(f'get_release_cache: {app_id} timeout!')


async def __get_release_cache(queue: ThreadQueue,
                              hub_uuid: str, auth: dict or None, app_id: dict) -> dict or None:
    try:
        release_cache = cache_manager.get_release_cache(hub_uuid, auth, app_id)
        queue.put((app_id, release_cache))
    except (KeyError, NameError):
        pass


def _get_release_nocache(queue: ThreadQueue, hub, app_id_list: list, auth: dict or None) -> Thread:
    thread = Thread(target=asyncio.run,
                    args=(__run_get_release_fun(queue, hub, app_id_list, auth),))
    thread.start()
    return thread


async def __run_get_release_fun(queue: ThreadQueue, hub, app_id_list: list, auth: dict or None):
    hub_uuid = hub.get_uuid()
    # noinspection PyBroadException
    try:
        if get_hub_available(hub_uuid):
            hub_core = hub.get_release_list(queue, app_id_list, auth)
            await __run_core(hub_core, len(app_id_list))
        set_hub_available(hub_uuid, True)
    except Exception:
        set_hub_available(hub_uuid, False)
    finally:
        queue.close()


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
