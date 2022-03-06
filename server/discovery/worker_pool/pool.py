import asyncio
import random
import time

import pynng

from config import node_activity_time
from ..client_utils import get_service_address_list


class Node:
    def __init__(self, address: str):
        sock = pynng.Req0()
        sock.dial(address)
        self.socket = sock
        self.time = time.time()

    def self_check(self) -> bool:
        if time.time() - self.time > node_activity_time:
            self.disconnect()
            return False
        else:
            return True

    def disconnect(self):
        self.socket.close()


pool_list: list[Node] = []
discovery_address = None
lock = asyncio.Lock()


def get_node() -> Node:
    with lock:
        return _get_node()


def _get_node() -> Node:
    node = _get_cache_node()
    if not node:
        node = _get_new_node()
    return node


def _get_cache_node() -> Node or None:
    node = random.choice(pool_list)
    if node.self_check():
        return node
    else:
        return None


def _get_new_node() -> Node:
    server_list = get_service_address_list(discovery_address)
    server_address = random.choice(server_list)
    node = Node(server_address)
    pool_list.append(node)
    return node
