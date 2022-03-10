import asyncio
import logging
import random
import time

import pynng

from config import node_activity_time, discovery_url
from ..client_utils import get_service_address_list


class Node:
    def __init__(self):
        self.socket = None
        self.time = None
        self.address = None

    def init_socket(self, address: str):
        self.address = address
        self.reconnect()

    def reconnect(self) -> bool:
        self.disconnect()
        sock = pynng.Req0()
        sock.dial(self.address)
        self.socket = sock
        self.time = time.time()
        return True

    def self_check(self) -> bool:
        if time.time() - self.time > node_activity_time:
            return self.reconnect()
        else:
            return True

    def disconnect(self):
        try:
            if self.socket:
                self.socket.close()
        except Exception as e:
            logging.error(e)


class Pool:
    discovery_address = discovery_url

    def __init__(self):
        self.node_list: list[Node] = []
        self.lock = asyncio.Lock()

    async def remove_node(self, node):
        async with self.lock:
            self.node_list.remove(node)

    async def get_node(self) -> Node or None:
        async with self.lock:
            return await self._get_node()

    async def _get_node(self) -> Node or None:
        node = self._get_cache_node()
        if not node:
            await self._renew_node_list()
            node = self._get_cache_node(False)
        return node

    def _get_cache_node(self, self_check=True) -> Node or None:
        if not self.node_list:
            return None
        node = random.choice(self.node_list)
        if not self_check:
            return node
        if node.self_check():
            return node
        else:
            self.node_list.remove(node)
            return None

    async def _get_new_node(self) -> Node or None:
        server_list = await get_service_address_list(self.discovery_address)
        server_address = random.choice(server_list)
        node = Node()
        node.init_socket(server_address)
        return node

    async def _renew_node_list(self):
        while len(self.node_list) <= 3:
            node = await self._get_new_node()
            self.node_list.append(node)
