from hashlib import md5

from pynng import Rep0, Req0


async def send_rep_with_id(socket: Rep0, msg_id, rep_msg: bytes) -> str:
    await socket.asend(msg_id + rep_msg)
    return msg_id


async def get_req_with_id(socket: Rep0) -> [str, bytes]:
    req = await socket.arecv_msg()
    req_bytes = req.bytes
    msg_id = req_bytes[:16]
    return msg_id, req.bytes[16:]


async def send_req_with_id(socket: Req0, msg: bytes) -> bytes:
    msg_id = md5(msg).digest()
    await socket.asend(msg_id + msg)
    return msg_id


async def get_rep_by_id(socket: Req0, msg_id=None, msg: bytes = None) -> bytes:
    if not msg_id:
        msg_id = md5(msg).digest()
    while True:
        req = await socket.arecv_msg()
        req_bytes = req.bytes
        req_id = req_bytes[:16]
        if req_id == msg_id:
            return req_bytes[16:]
