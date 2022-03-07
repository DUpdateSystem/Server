import asyncio
import time

import pynng

from config import node_activity_time
from utils.logging import logging
from .constant import GET_SERVICE_ADDRESS, REGISTER_SERVICE_ADDRESS
from .muti_reqrep import send_req_with_id, get_rep_by_id


def get_ttl_hash():
    """Return the same value withing `seconds` time period"""
    return round(time.time() / node_activity_time)


async def keep_register_service_address_list(address, self_address_list):
    with pynng.Req0() as sock:
        sock.dial(address)
        while True:
            for self_address in self_address_list:
                await _register_service_address(sock, self_address)
            await asyncio.sleep(node_activity_time / 2)


async def keep_register_service_address(address, self_address):
    with pynng.Req0() as sock:
        sock.dial(address)
        while True:
            await _register_service_address(sock, self_address)
            await asyncio.sleep(node_activity_time / 2)


async def _register_service_address(sock, self_address):
    data = f"{REGISTER_SERVICE_ADDRESS} {self_address}".encode()
    await send_req_with_id(sock, data)


# noinspection PyUnusedLocal
# @alru_cache(maxsize=1)
async def get_service_address_list(address, ttl_hash=get_ttl_hash()) -> list[str]:
    with pynng.Req0() as sock:
        sock.dial(address)
        msg_id = await send_req_with_id(sock, GET_SERVICE_ADDRESS.encode())
        msg = await get_rep_by_id(sock, msg_id)
        service_address_list = msg.decode().split(' ')
        if not service_address_list:
            logging.warning("get_service_address_list: empty service list")
        return service_address_list
