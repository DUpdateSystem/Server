import asyncio
import hashlib
import time
from async_lru import alru_cache

import pynng

from config import node_activity_time
from utils.logging import logging
from .constant import GET_SERVICE_ADDRESS, REGISTER_SERVICE_ADDRESS


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
    await sock.asend(f"{REGISTER_SERVICE_ADDRESS} {self_address}".encode())


# noinspection PyUnusedLocal
# @alru_cache(maxsize=1)
async def get_service_address_list(address, ttl_hash=get_ttl_hash()) -> list[str]:
    with pynng.Req0() as sock:
        sock.dial(address)
        await sock.asend(GET_SERVICE_ADDRESS.encode())
        msg = await sock.arecv_msg()
        service_address_list = msg.bytes.decode().split(' ')
        if not service_address_list:
            logging.warning("get_service_address_list: empty service list")
        return service_address_list
