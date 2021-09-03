import asyncio

from socketio import AsyncClient, AsyncClientNamespace

from app.server.config import server_config
from app.server.manager.data.constant import logging
from .double_sided_api import DoubleSidedApi
from app.cluster.manager.finder import add_server_node, del_server_node


# noinspection PyMethodMayBeStatic
class StatusConnectNamespace(AsyncClientNamespace, DoubleSidedApi):

    def __init__(self, host: str, namespace: str):
        super().__init__(namespace=namespace)
        self.host = host

    async def on_connect(self):
        print("I'm connected!")

    async def on_disconnect(self):
        print("I'm disconnected!")

    async def on_connect_error(self, data):
        logging.info(data)

    async def on_node_get_server_port(self):
        return server_config.port


class ClientContainer:
    sio = AsyncClient()

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        self.sio.register_namespace(StatusConnectNamespace(f'{ip}:{port}', '/status'))

    @staticmethod
    @sio.event
    def connect_error(data):
        print("The connection failed!")

    async def connect(self):
        # noinspection HttpUrlsUsage
        await self.sio.connect(f'http://{self.ip}:{self.port}', namespaces=['/status'])
        add_server_node(self.ip, self.port, self.sio)

    async def disconnect(self):
        await self.sio.disconnect()
        del_server_node(self.ip, self.port)


asyncio.run(ClientContainer('localhost', 5256).connect())
