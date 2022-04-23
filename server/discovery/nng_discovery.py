import asyncio
import random
import time

import pynng
from nng_wrapper.muti_reqrep import get_req_with_id, send_rep_with_id
from utils.logging import logging

from .config import node_activity_time
from .constant import GET_SERVICE_ADDRESS, REGISTER_SERVICE_ADDRESS

_service_address_map = {}
__map_lock = asyncio.Lock()


async def bind_node_service(listen_address):
    with pynng.Rep0() as sock:
        sock.listen(listen_address)
        while True:
            try:
                await _bind_node_service(sock)
            except TimeoutError:
                continue


async def _bind_node_service(sock: pynng.Rep0):
    msg_id, request = await get_req_with_id(sock)
    content = request.decode()
    logging.info("discovery req " + content)
    data = await _msg_handle(content)
    if data:
        await send_rep_with_id(sock, msg_id, data)


async def _register_service(address: str):
    async with __map_lock:
        logging.info(f"register_service: {address}")
        _service_address_map[address] = time.time()


async def _get_service_address_list() -> list[str]:
    async with __map_lock:
        return __get_service_address_list()


def __get_service_address_list() -> list[str]:
    now_time = time.time()
    service_address_list = []
    for address, register_time in _service_address_map.copy().items():
        if now_time - register_time <= node_activity_time:
            service_address_list.append(address)
        else:
            del _service_address_map[address]
            logging.info(f"nng_discovery: inactivity(del): {address}")
    return service_address_list


async def _msg_handle(msg: str) -> bytes or None:
    key = msg[:3]
    body = msg[3:]
    if GET_SERVICE_ADDRESS == key:
        list_size = 0
        if body:
            list_size = int(body)
        service_address_list = await _get_service_address_list()
        if list_size:
            service_address_list = random.choices(
                service_address_list,
                k=min(list_size, len(service_address_list)))
        date = ' '.join(service_address_list)
        return date.encode()
    elif REGISTER_SERVICE_ADDRESS == key:
        _service_address_map[body] = time.time()


async def _main(node_listen_address: str):
    await bind_node_service(node_listen_address)


def main(node_listen_address: str):
    asyncio.run(_main(node_listen_address))
