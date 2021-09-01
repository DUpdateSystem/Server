import asyncio

from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging
from app.server.utils.queue import LightQueue
from app.status_checker.status import set_hub_available, get_hub_available


async def get_release(hub_uuid: str, auth: dict or None, app_id: dict, use_cache=True, cache_data=True) -> dict or None:
    from app.server.hubs.hub_list import hub_dict
    hub = hub_dict[hub_uuid]
    if use_cache:
        release_list = await __get_release_cache_async_container(hub_uuid, auth, app_id)
        if release_list is not None and not (len(release_list) == 1 and release_list[0] is None):
            return release_list
    observer_queue = LightQueue()
    await __run_get_release_fun(observer_queue, hub, [app_id], auth)
    item: dict = await observer_queue.get()
    try:
        release_list = item["v"]
    except TypeError:
        return None
    if cache_data and release_list is not None:
        cache_manager.add_release_cache(hub_uuid, auth, app_id, release_list)
    return release_list


async def get_release_list(return_queue: LightQueue, hub_uuid: str, auth: dict or None, app_id_list: list,
                           use_cache=True, cache_data=True):
    from app.server.hubs.hub_list import hub_dict
    hub = hub_dict[hub_uuid]
    observer_queue = LightQueue()
    if use_cache:
        asyncio.create_task(__get_release_cache_async(observer_queue, hub_uuid, auth, app_id_list))
        async for app_id, release_list in observer_queue:
            if release_list is not None and not (len(release_list) == 1 and release_list[0] is None):
                await return_queue.put((hub_uuid, auth, app_id, use_cache, release_list))
                app_id_list.remove(app_id)
    if app_id_list:
        asyncio.create_task(__run_get_release_fun(observer_queue, hub, app_id_list, auth))
        async for item in observer_queue:
            app_id = item["id"]
            release_list = item["v"]
            await return_queue.put((hub_uuid, auth, app_id, use_cache, release_list))
            if cache_data:
                if release_list is not None:
                    cache_manager.add_release_cache(hub_uuid, auth, app_id, release_list)


async def __get_release_cache_async(queue: LightQueue, hub_uuid: str, auth: dict or None, app_id_list: list):
    core_list = [__get_release_cache_async_container(queue, hub_uuid, auth, app_id) for app_id in app_id_list]
    await asyncio.gather(*core_list)
    await queue.close()


async def __get_release_cache_async_container(hub_uuid: str, auth: dict or None, app_id: dict) -> dict or None:
    try:
        return await __run_core(__get_release_cache(hub_uuid, auth, app_id), 1, True)
    except asyncio.TimeoutError:
        logging.info(f'get_release_cache: {app_id} timeout!')


async def __get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> dict or None:
    try:
        return cache_manager.get_release_cache(hub_uuid, auth, app_id)
    except (KeyError, NameError):
        pass


async def __run_get_release_fun(queue: LightQueue, hub, app_id_list: list, auth: dict or None):
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
        await queue.close()


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
