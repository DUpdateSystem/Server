import asyncio
from multiprocessing import Process, Event

from app.server.utils.queue import LightQueue
from app.server.utils.utils import set_new_asyncio_loop
from .release_getter import get_release
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
        queue = LightQueue()
        loop.create_task(self.__callback(queue))
        loop.run_until_complete(self.__run_getter(queue))
        loop.close()

    async def __run_getter(self, queue: LightQueue):
        while not self.stop_event.is_set():
            print("wait get")
            item = request_list.pop_request_list()
            if item is None:
                return
            hub_uuid, auth, use_cache, app_id_list = item
            print("get" + str(app_id_list))
            await asyncio.create_task(get_release(queue, hub_uuid, auth, app_id_list, use_cache))

    @staticmethod
    async def __callback(queue: LightQueue):
        while True:
            print("ping")
            item = await queue.get()
            if item is EOFError:
                break
            print(len(item))
            hub_uuid, auth, app_id, use_cache, release_list = item
            print("callback")
            request_list.callback_request(hub_uuid, auth, app_id, use_cache, release_list)


request_polling = RequestPolling()
