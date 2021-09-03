from aiohttp.web import Application
from socketio import AsyncServer, AsyncNamespace

from .double_sided_api import DoubleSidedApi
from app.cluster.manager.finder import add_client_node, del_node_sid, set_node_hub_reliability_sid

sio = AsyncServer(async_mode='aiohttp')


# noinspection PyMethodMayBeStatic
class StatusConnectNamespace(AsyncNamespace, DoubleSidedApi):

    async def on_connect(self, sid, environ):
        ip = environ['REMOTE_ADDR']
        await self.emit('node_get_server_port', callback=lambda port: add_client_node(ip, port, sid))
        await self.emit('self_get_available_hub',
                        callback=lambda reliability_hub: set_node_hub_reliability_sid(sid, reliability_hub))

    async def on_disconnect(self, sid):
        del_node_sid(sid)

    async def on_connect_error(self, sid):
        del_node_sid(sid)


sio.register_namespace(StatusConnectNamespace('/status'))

app = Application()
sio.attach(app)
