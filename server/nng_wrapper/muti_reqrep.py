from hashlib import md5

from pynng import Rep0, Req0

from .reqrep import asend, arecv_msg


async def send_rep_with_id(socket: Rep0, msg_id, rep_msg: bytes) -> str:
    await asend(socket, msg_id + rep_msg)
    return msg_id


async def send_req_with_id(socket: Req0, msg: bytes) -> bytes:
    msg_id = md5(msg).digest()
    await asend(socket, msg_id + msg)
    return msg_id


async def get_req_with_id(socket: Rep0) -> [str, bytes]:
    req = await arecv_msg(socket)
    return _get_req_with_id(req)


def _get_req_with_id(req_bytes) -> [str, bytes]:
    msg_id = req_bytes[:16]
    return msg_id, req_bytes[16:]


async def get_rep_by_id(socket: Req0, msg_id=None, msg: bytes = None) -> bytes:
    if not msg_id:
        msg_id = md5(msg).digest()
    while True:
        req = await arecv_msg(socket)
        req_bytes = req
        req_id = req_bytes[:16]
        if req_id == msg_id:
            return req_bytes[16:]
