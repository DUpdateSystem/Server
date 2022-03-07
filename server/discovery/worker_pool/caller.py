from .pool import Pool
from ..muti_reqrep import send_req_with_id, get_rep_by_id

pool = Pool()


async def send_req(msg: bytes) -> bytes:
    node = await pool.get_node()
    sock = node.socket
    msg_id = await send_req_with_id(sock, msg)
    return await get_rep_by_id(sock, msg_id)
