import asyncio
from threading import Thread
from time import sleep

from app.server.utils.utils import set_new_asyncio_loop
from .getter_request_list import getter_request_list
from .getter_utils import get_release


class WebGetterManager:
    thread: Thread or None = None

    def start(self) -> Thread:
        if not self.thread:
            self.thread = Thread(target=self._run_getter)
            self.thread.start()
        return self.thread

    def join(self, timeout=None):
        if self.thread:
            self.thread.join(timeout)

    def send_request(self, hub_uuid: str, auth: dict, app_id: dict, callback, use_cache: bool = True):
        getter_request_list.add_request(hub_uuid, auth, app_id, callback, use_cache)
        self.start()

    def _run_getter(self):
        loop = set_new_asyncio_loop()
        loop.run_until_complete(self.__run_getter(loop))
        loop.close()
        self.thread = None

    async def __run_getter(self, loop):
        while not getter_request_list.is_empty():
            await asyncio.sleep(1)
            hub_uuid, auth, use_cache, app_id_list = getter_request_list.pop_request_list()
            loop.create_task(self.__do_getter(hub_uuid, auth, use_cache, app_id_list))
            await asyncio.sleep(2)

    @staticmethod
    async def __do_getter(hub_uuid: str, auth: dict, use_cache: bool, app_id_list: list):
        iter_core = get_release(hub_uuid, app_id_list, auth, use_cache)
        for app_id, release_list in iter_core:
            getter_request_list.callback_request(hub_uuid, auth, use_cache, app_id, release_list)


web_getter_manager = WebGetterManager()
