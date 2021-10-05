import asyncio
import json
from threading import Thread, Lock

import zmq
import zmq.asyncio

from database.cache_manager import cache_manager
from getter.net_getter.cloud_config_getter import get_cloud_config_str
from getter.net_getter.download_getter import get_download_info_list
from getter.net_getter.release_getter import get_single_release
from proxy.format.header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST
from proxy.format.zmq_request_format import load_release_request, load_download_request, load_cloud_config_request
from utils.asyncio import run_with_time_limit
from utils.logging import logging


async def worker_routine(worker_url: str):
    context = zmq.asyncio.Context()
    socket: zmq.asyncio.Socket = context.socket(zmq.REP)
    socket.connect(worker_url)
    cache_manager.connect()

    while True:
        up_worker_num()
        request_str = await socket.recv_string()
        down_worker_num()
        overload_throw_proxy(worker_url)
        try:
            value = await run_with_time_limit(do_work(request_str), 45)
            response = json.dumps(value)
        except Exception as e:
            logging.exception(e)
            response = json.dumps(None)
        await socket.send_string(response)

    # cache_manager.disconnect()


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
    release_list = get_single_release(hub_uuid, auth, app_id, use_cache, cache_data)
    return release_list


async def get_download_info(hub_uuid: str, auth: dict, app_id: list, asset_index: list):
    download_info = await get_download_info_list(hub_uuid, auth, app_id, asset_index)
    return download_info


async def get_cloud_config(dev_version: bool, migrate_master: bool):
    cloud_config = get_cloud_config_str(dev_version, migrate_master)
    return cloud_config


async_worker_num = 10  # 并行协程数
thread_worker_num = 3  # 并行线程数

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
    logging.info(f"getter overload_throw: disable")


async def main(worker_url: str):
    async_worker_list = []
    for _ in range(async_worker_num):
        async_worker_list.append(worker_routine(worker_url))
    await asyncio.gather(*async_worker_list)


def run_single(worker_url: str):
    asyncio.run(main(worker_url))


def run():
    worker_url = 'tcp://upa-proxy:5560'
    cache_manager.init()
    for _ in range(thread_worker_num):
        Thread(target=run_single, args=(worker_url,)).start()
