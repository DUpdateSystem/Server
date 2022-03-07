from .pool import get_node
from ..muti_reqrep import send_req_with_id, get_rep_by_id


async def send_req(msg: bytes) -> bytes:
    node = await get_node()
    sock = node.socket
    msg_id = await send_req_with_id(sock, msg)
    return await get_rep_by_id(sock, msg_id)
