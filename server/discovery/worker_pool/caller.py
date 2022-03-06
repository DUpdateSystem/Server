from .pool import get_node


async def get_msg(msg):
    node = get_node()
    sock = node.socket
    await sock.asend_msg(msg)
    return await sock.arecv_msg()
