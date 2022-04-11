from utils.logging import logging
from .pool import Pool
from nng_wrapper.muti_reqrep import send_req_with_id, get_rep_by_id

pool = Pool()

AUTO_RETRY_NUM = 3


async def send_req(msg: bytes) -> bytes or None:
    for _ in range(AUTO_RETRY_NUM):
        node = await pool.get_node()
        try:
            return await _send_req(node, msg)
        except Exception as e:
            logging.error(e)
            await pool.remove_node(node)


async def _send_req(node, msg) -> bytes or None:
    return await __send_req(node, msg)


async def __send_req(node, msg) -> bytes:
    sock = node.socket
    msg_id = await send_req_with_id(sock, msg)
    return await get_rep_by_id(sock, msg_id)
