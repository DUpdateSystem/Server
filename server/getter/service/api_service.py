import asyncio
import json
import time
from threading import Thread, Lock

import pynng

from config import node_activity_time, discovery_url
from database.cache_manager import cache_manager
from discovery.client_utils import register_service_address
from nng_wrapper.format.header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST
from nng_wrapper.format.zmq_request_format import load_release_request, load_download_request, load_cloud_config_request
from nng_wrapper.muti_reqrep import get_req_with_id, send_rep_with_id
from utils.logging import logging
from .api import get_cloud_config_str, get_single_release, get_download_info_list


async def worker_routine(worker_url: str):
    lock = asyncio.Lock()
    while True:
        try:
            await asyncio.gather(
                _worker_routine(worker_url, lock),
                register_worker(worker_url, lock),
            )
        except Exception as e:
            logging.exception(e)


async def register_worker(worker_url, lock: asyncio.Lock):
    time_s = 0
    while True:
        if time.time() - time_s > node_activity_time:
            async with lock:
                await register_service_address(discovery_url, worker_url)
                time_s = time.time()
        await asyncio.sleep(node_activity_time / 20)


async def _worker_routine(worker_url: str, lock: asyncio.Lock):
    while True:
        try:
            await __worker_routine(worker_url, lock)
        except Exception as e:
            logging.exception(e)


async def __worker_routine(worker_url: str, lock: asyncio.Lock):
    with pynng.Rep0() as socket:
        socket.listen(worker_url)
        while True:
            try:
                msg_id, request = await get_req_with_id(socket)
                async with lock:
                    request_str = request.decode()
                    logging.info("getter req " + request_str)
                    value = await do_work(request_str)
                    response = json.dumps(value)
            except TimeoutError:
                logging.warning("timeout")
            except Exception as e:
                logging.exception(e)
                response = json.dumps(None)
            finally:
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


async def get_release(hub_uuid: str, auth: dict or None, app_id: dict, use_cache=True, cache_data=True):
    release_list = get_single_release(hub_uuid, auth, app_id, use_cache)
    return release_list


async def get_download_info(hub_uuid: str, auth: dict, app_id: list, asset_index: list):
    download_info = await get_download_info_list(hub_uuid, auth, app_id, asset_index)
    return download_info


async def get_cloud_config(dev_version: bool, migrate_master: bool):
    cloud_config = get_cloud_config_str(dev_version, migrate_master)
    return cloud_config


worker_num = 0
worker_count_lock = Lock()


def up_worker_num():
    with worker_count_lock:
        global worker_num
        worker_num += 1


def down_worker_num():
    with worker_count_lock:
        global worker_num
        worker_num -= 1


def get_worker_num():
    with worker_count_lock:
        return worker_num


overload_throw_lock = Lock()


def overload_throw_proxy(worker_url: str):
    with overload_throw_lock:
        if get_worker_num() <= 0:
            overload_throw(worker_url)


def overload_throw(worker_url: str):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.connect(worker_url)
    logging.info(f"getter overload_throw: enable")
    while get_worker_num() <= 0:
        requests = socket.recv_string()
        logging.info(f"getter overload_throw: {requests}")
        socket.send_string(json.dumps(None))
    socket.close()
    context.term()
    logging.info(f"getter overload_throw: disable")


async def async_run(worker_url_list: str):
    async_worker_list = []
    for worker_url in worker_url_list:
        async_worker_list.append(worker_routine(worker_url))
    await asyncio.gather(*async_worker_list)


def _run(worker_url: str):
    asyncio.run(async_run(worker_url))


def run(worker_url_list) -> list[Thread]:
    cache_manager.init()
    t_list = []
    for worker_async_url_list in worker_url_list:
        t = Thread(target=_run, args=(worker_async_url_list,))
        t.start()
        t_list.append(t)
    return t_list
