import asyncio
import hashlib
import time
from functools import lru_cache

import pynng

from config import node_activity_time
from utils.logging import logging
from .constant import GET_SERVICE_ADDRESS, REGISTER_SERVICE_ADDRESS


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
    await sock.asend(REGISTER_SERVICE_ADDRESS + ' ' + self_address.encode())


async def get_service_address_list(address) -> list[str]:
    with pynng.Req0() as sock:
        sock.dial(address)
        await sock.asend(GET_SERVICE_ADDRESS.encode())
        msg = await sock.arecv_msg()
        service_address_list = msg.bytes.decode().split(' ')
        if not service_address_list:
            logging.warning("get_service_address_list: empty service list")
        return service_address_list


async def _call_service_node(msg, service_discovery_address):
    service_list = await get_service_address_list(service_discovery_address)
    i = hashlib.md5(msg.encode('utf8')).digest()[0]
    node_address = service_list[i]
    with pynng.Req0() as sock:
        sock.dial(node_address)
        await sock.asend(msg.encode())
        resp = await sock.arecv_msg()
        return resp.bytes.decode()


def get_ttl_hash():
    """Return the same value withing `seconds` time period"""
    return round(time.time() / node_activity_time)


# noinspection PyUnusedLocal
@lru_cache(maxsize=1)
async def call_service_node(msg, service_discovery_address, ttl_hash=get_ttl_hash()):
    del ttl_hash
    return await _call_service_node(msg, service_discovery_address)
