import asyncio
import json
from threading import Thread, Lock

import pynng

from config import timeout_getter
from database.cache_manager import cache_manager
from getter.net_getter.cloud_config_getter import get_cloud_config_str
from getter.net_getter.download_getter import get_download_info_list
from getter.net_getter.release_getter import get_single_release
from proxy.format.header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST
from proxy.format.zmq_request_format import load_release_request, load_download_request, load_cloud_config_request, \
    check_time
from utils.asyncio import run_with_time_limit
from utils.logging import logging


async def worker_routine(worker_url: str):
    with pynng.Rep0() as socket:
        socket.listen(worker_url)
        while True:
            request = await socket.arecv_msg()
            request_str = request.bytes.decode()
            try:
                value = await run_with_time_limit(do_work(request_str), timeout_getter)
                response = json.dumps(value)
            except Exception as e:
                logging.exception(e)
                response = json.dumps(None)
            await socket.send_string(response)


async def do_work(request_str: str):
    if not check_time(request_str):
        return
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
    release_list = get_single_release(hub_uuid, auth, app_id, use_cache, cache_data)
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


def run(worker_url_list):
    cache_manager.init()
    for worker_async_url_list in worker_url_list:
        Thread(target=_run, args=(worker_async_url_list,)).start()
