import logging

from .pool import Pool
from ..muti_reqrep import send_req_with_id, get_rep_by_id

pool = Pool()


async def send_req(msg: bytes) -> bytes or None:
    node = await pool.get_node()
    try:
        return await _send_req(node, msg)
    except Exception as e:
        logging.error(e)
        try:
            value = await _send_req(node, msg, True)
            if value is None:
                pool.remove_node(node)
        except Exception as e:
            logging.error(e)
            pool.remove_node(node)


async def _send_req(node, msg, reconnect=False) -> bytes or None:
    if reconnect and node.reconnect():
        return await _send_req(node, msg)
    else:
        return None


async def __send_req(node, msg) -> bytes:
    sock = node.socket
    msg_id = await send_req_with_id(sock, msg)
    return await get_rep_by_id(sock, msg_id)
