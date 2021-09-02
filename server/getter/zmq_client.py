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


async def worker_routine(worker_url: str):
    context = zmq.asyncio.Context()
    socket: zmq.asyncio.Socket = context.socket(zmq.REP)
    socket.connect(worker_url)

    while True:
        request_str = await socket.recv_string()
        request_key = request_str[0]
        if request_key == RELEASE_REQUEST:
            args = load_release_request(request_str)
            asyncio.create_task(get_release(socket, *args))
        elif request_key == DOWNLOAD_REQUEST:
            args = load_download_request(request_str)
            asyncio.create_task(get_download_info(socket, *args))
        elif request_key == CLOUD_CONFIG_REQUEST:
            args = load_cloud_config_request(request_str)
            asyncio.create_task(get_cloud_config(socket, *args))


async def get_release(socket, hub_uuid: str, auth: dict or None, app_id: dict, use_cache=True, cache_data=True):
    release_list = await get_single_release(hub_uuid, auth, app_id, use_cache, cache_data)
    await socket.send_string(json.dumps(release_list))


async def get_download_info(socket, hub_uuid: str, auth: dict, app_id: list, asset_index: list):
    download_info = await get_download_info_list(hub_uuid, auth, app_id, asset_index)
    await socket.send_string(json.dumps(download_info))


async def get_cloud_config(socket, dev_version: bool, migrate_master: bool):
    cloud_config = get_cloud_config_str(dev_version, migrate_master)
    await socket.send_string(json.dumps(cloud_config))


async_worker_num = 3
thread_worker_num = 3


async def main():
    worker_url = 'tcp://localhost:5560'
    await asyncio.gather(*[worker_routine(worker_url)] * async_worker_num)


def run_single():
    cache_manager.init()
    cache_manager.connect()
    asyncio.run(main())


def run():
    for _ in range(thread_worker_num):
        Thread(target=run_single, ).start()
