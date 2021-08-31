import asyncio
from multiprocessing import Process, Event

from app.server.utils.utils import set_new_asyncio_loop
from .getter_utils import get_release
from .request_list import request_list


class RequestPolling:
    process: Process or None = None
    stop_event = Event()

    def start(self) -> Process:
        if not self.process:
            self.process = Process(target=self._run_getter)
            self.process.start()
        return self.process

    def join(self, timeout=None):
        if self.process:
            self.process.join(timeout)

    def kill(self):
        self.process.kill()

    def stop(self):
        self.stop_event.set()
        request_list.wait_event.set()

    def send_request(self, hub_uuid: str, auth: dict, app_id: dict, callback, use_cache: bool = True):
        request_list.add_request(hub_uuid, auth, app_id, callback, use_cache)

    def _run_getter(self):
        loop = set_new_asyncio_loop()
        loop.run_until_complete(self.__run_getter())
        loop.close()

    async def __run_getter(self):
        while not self.stop_event.is_set():
            await asyncio.sleep(1)
            print("wait get")
            item = request_list.pop_request_list()
            if item is None:
                return
            hub_uuid, auth, use_cache, app_id_list = item
            print("get" + str(app_id_list))
            await asyncio.create_task(self.__do_getter(hub_uuid, auth, use_cache, app_id_list))
            await asyncio.sleep(2)

    @staticmethod
    async def __do_getter(hub_uuid: str, auth: dict, use_cache: bool, app_id_list: list):
        iter_core = get_release(hub_uuid, app_id_list, auth, use_cache)
        for app_id, release_list in iter_core:
            request_list.callback_request(hub_uuid, auth, use_cache, app_id, release_list)


request_polling = RequestPolling()
