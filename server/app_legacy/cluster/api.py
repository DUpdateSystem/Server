from asyncio import Lock

from socketio import AsyncClient

from .manager.connect_manager import get_random_node


def get_release_list(hub_uuid, auth, app_id):
    node = get_random_node()
    lock = Lock()
    release_list = []
    lock.acquire()
    if type(node) is AsyncClient:
        node: AsyncClient
        # TODO: need fix
        node.emit('hub_get_app_release_list', data=(hub_uuid, auth, app_id), namespace='/',
                  callback=lambda _release_list: release_list.__add__(_release_list) and lock.release())
