import asyncio
import random
import time

import pynng
from utils.logging import logging

from ..client_utils import get_service_address_list
from ..config import node_activity_time


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
        return time.time() - self.time <= node_activity_time * 2

    def disconnect(self):
        try:
            if self.socket:
                self.socket.close()
        except Exception as e:
            logging.error(e)


class Pool:
    wocker_list_size = 8

    def __init__(self, discovery_url):
        self.discovery_address = discovery_url
        self.node_list: list[Node] = []
        self.lock = asyncio.Lock()

    async def remove_node(self, node):
        async with self.lock:
            await self._remove_node(node)

    async def get_node(self) -> Node or None:
        async with self.lock:
            return await self._get_node()

    async def _get_node(self) -> Node or None:
        node = None
        while not node:
            node = await self.__get_node()
        return node

    async def __get_node(self) -> Node or None:
        less_list_size = self.wocker_list_size - len(self.node_list)
        if less_list_size >= len(self.node_list):
            await self._renew_node_list(less_list_size)
        node = random.choice(self.node_list)
        return node

    async def _remove_node(self, node):
        node.socket.close()
        self.node_list.remove(node)

    async def _renew_node_list(self, list_size) -> Node or None:
        server_list = await get_service_address_list(self.discovery_address,
                                                     list_size=list_size)
        for server_address in server_list:
            node = Node()
            node.init_socket(server_address)
            self.node_list.append(node)
