import asyncio
import json
import time
from threading import Event, Thread

import pynng
from database.cache_manager import cache_manager
from discovery.client_utils import register_service_address
from nng_wrapper.format.header_key import (CLOUD_CONFIG_REQUEST,
                                           DOWNLOAD_REQUEST, RELEASE_REQUEST)
from nng_wrapper.format.zmq_request_format import (load_cloud_config_request,
                                                   load_download_request,
                                                   load_release_request)
from nng_wrapper.muti_reqrep import get_req_with_id, send_rep_with_id
from nng_wrapper.socket_builder import rep0, req0
from utils.logging import logging

from .api import (get_cloud_config_str, get_download_info_list,
                  get_single_release)

run_event = Event()

node_activity_time = 15


async def worker_run(discovery_url, worker_url: str):
    lock = asyncio.Lock()
    await asyncio.gather(
        _worker_routine(worker_url, lock),
        _register_worker(discovery_url, worker_url, lock),
    )
    logging.warning(f"stop: {worker_url}")


async def _register_worker(discovery_url, worker_url, lock: asyncio.Lock):
    time_s = 0
    while not run_event.is_set():
        if time.time() - time_s > node_activity_time:
            async with lock:
                try:
                    with req0(discovery_url) as sock:
                        await register_service_address(sock, worker_url)
                    time_s = time.time()
                except pynng.exceptions.Timeout:
                    pass
                except Exception as e:
                    logging.exception(e)
        await asyncio.sleep(node_activity_time / 20)
    logging.warning(f"stop register: {worker_url}")


async def _worker_routine(worker_url: str, lock: asyncio.Lock):
    while not run_event.is_set():
        try:
            await __worker_routine(worker_url, lock)
        except Exception as e:
            logging.exception(e)
    logging.warning(f"stop worker: {worker_url}")


async def __worker_routine(worker_url: str, lock: asyncio.Lock):
    with rep0(worker_url) as socket:
        while not run_event.is_set():
            msg_id = None
            try:
                msg_id, request = await get_req_with_id(socket)
                async with lock:
                    request_str = request.decode()
                    logging.info("getter req " + request_str)
                    value = await do_work(request_str)
                    response = json.dumps(value)
            except pynng.exceptions.Timeout:
                pass
            except TimeoutError:
                logging.warning("timeout")
            except Exception as e:
                logging.exception(e)
                response = json.dumps(None)
            finally:
                if msg_id:
                    await send_rep_with_id(socket, msg_id, response.encode())


async def do_work(request_str: str):
    request_key = request_str[0]
    if request_key == RELEASE_REQUEST:
        args = load_release_request(request_str)
        return await get_release(*args)
    elif request_key == DOWNLOAD_REQUEST:
        args = load_download_request(request_str)
        return await get_download_info(*args)
    elif request_key == CLOUD_CONFIG_REQUEST:
        args = load_cloud_config_request(request_str)
        return await get_cloud_config(*args)


async def get_release(hub_uuid: str,
                      auth: dict or None,
                      app_id: dict,
                      use_cache=True,
                      cache_data=True):
    release_list = get_single_release(hub_uuid, auth, app_id, use_cache)
    return release_list


async def get_download_info(hub_uuid: str, auth: dict, app_id: list,
                            asset_index: list):
    download_info = await get_download_info_list(hub_uuid, auth, app_id,
                                                 asset_index)
    return download_info


async def get_cloud_config(dev_version: bool, migrate_master: bool):
    cloud_config = get_cloud_config_str(dev_version, migrate_master)
    return cloud_config


async def async_run(discovery_url, worker_url_list):
    async_worker_list = []
    for worker_url in worker_url_list:
        async_worker_list.append(worker_run(discovery_url, worker_url))
    await asyncio.gather(*async_worker_list)


def _run(discovery_url, worker_url_list: str):
    asyncio.run(async_run(discovery_url, worker_url_list))


def run(discovery_url, worker_url_list) -> list[Thread]:
    cache_manager.init()
    t_list = []
    for worker_async_url_list in worker_url_list:
        t = Thread(target=_run,
                   args=(
                       discovery_url,
                       worker_async_url_list,
                   ),
                   daemon=True)
        t.start()
        t_list.append(t)
    return t_list
