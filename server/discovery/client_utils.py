from os import environ
from urllib.parse import urlparse

import pynng
from nng_wrapper.muti_reqrep import get_rep_by_id, send_req_with_id
from utils.logging import logging

from .constant import GET_SERVICE_ADDRESS, REGISTER_SERVICE_ADDRESS


async def register_service_address(sock, self_address):
    parsed = urlparse(self_address)
    if 'ip' in environ:
        parsed = parsed._replace(
            netloc="{}:{}".format(environ['ip'], parsed.port))
    address = parsed.geturl()
    data = f"{REGISTER_SERVICE_ADDRESS}{address}".encode()
    await send_req_with_id(sock, data)


async def get_service_address_list(address, list_size=0) -> list[str]:
    with pynng.Req0() as sock:
        sock.dial(address)
        if list_size:
            list_size_str = list_size
        else:
            list_size_str = ''
        msg = f"{GET_SERVICE_ADDRESS}{list_size_str}"
        msg_id = await send_req_with_id(sock, msg.encode())
        msg = await get_rep_by_id(sock, msg_id)
        service_address_list = msg.decode().split(' ')
        if not service_address_list:
            logging.warning("get_service_address_list: empty service list")
        return service_address_list
