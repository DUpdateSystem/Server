import asyncio
import json
from threading import Thread

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

    while True:
        request_str = await socket.recv_string()
        try:
            value = await run_with_time_limit(do_work(request_str), 45)
            await socket.send_string(json.dumps(value))
        except Exception as e:
            logging.exception(e)
            await socket.send_string(json.dumps(None))


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


async_worker_num = 32
thread_worker_num = 1  # 暂时使用单线程查询，后期优化考虑线程池


async def main():
    worker_url = 'tcp://upa-proxy:5560'
    await asyncio.gather(*[worker_routine(worker_url)] * async_worker_num)


def run_single():
    cache_manager.connect()
    asyncio.run(main())


def run():
    cache_manager.init()
    for _ in range(thread_worker_num):
        Thread(target=run_single, ).start()
