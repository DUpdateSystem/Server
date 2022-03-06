from .pool import get_node


async def get_msg(msg):
    node = await get_node()
    sock = node.socket
    await sock.asend(msg)
    return await sock.arecv_msg()
