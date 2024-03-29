from random import choice

from nng_wrapper.muti_reqrep import get_rep_by_id, send_req_with_id
from utils.logging import logging

from .pool import Pool

AUTO_RETRY_NUM = 3

pool_list = []


def add_pool(discovery_url):
    pool = Pool(discovery_url)
    pool_list.append(pool)


async def send_req(msg: bytes) -> bytes or None:
    pool = choice(pool_list)
    return await _send_req(msg, pool)


async def _send_req(msg: bytes, pool: Pool) -> bytes or None:
    for _ in range(AUTO_RETRY_NUM):
        node = await pool.get_node()
        try:
            return await __send_req(node, msg)
        except Exception as e:
            logging.error(e)
            await pool.remove_node(node)


async def __send_req(node, msg) -> bytes:
    sock = node.socket
    msg_id = await send_req_with_id(sock, msg)
    return await get_rep_by_id(sock, msg_id)
