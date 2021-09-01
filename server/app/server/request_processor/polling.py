import asyncio
from multiprocessing import Process, Event
from threading import Thread

from app.server.utils.queue import LightQueue
from app.server.utils.utils import set_new_asyncio_loop, call_fun_in_loop
from .release_getter import get_release
from app.server.manager.cache_manager import cache_manager
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

    def _start_queue_convert(self, loop) -> LightQueue:
        queue = LightQueue(loop=loop)
        Thread(target=self._queue_converter, args=(loop, queue)).start()
        return queue

    def _queue_converter(self, loop, queue: LightQueue):
        while not self.stop_event.is_set():
            item = request_list.pop_request_list()
            call_fun_in_loop(queue.put(item), loop)

    def _run_getter(self):
        loop = set_new_asyncio_loop()
        queue = LightQueue()
        loop.create_task(self.__callback(queue))
        request_queue = self._start_queue_convert(loop)
        loop.run_until_complete(self.__run_getter(queue, request_queue))
        loop.close()

    async def __run_getter(self, queue: LightQueue, request_queue: LightQueue):
        cache_manager.init_db()
        while not self.stop_event.is_set():
            async for hub_uuid, auth, use_cache, app_id_list in request_queue:
                asyncio.create_task(get_release(queue, hub_uuid, auth, app_id_list, use_cache))
        cache_manager.disconnect()

    @staticmethod
    async def __callback(queue: LightQueue):
        while True:
            async for hub_uuid, auth, app_id, use_cache, release_list in queue:
                request_list.callback_request(hub_uuid, auth, app_id, use_cache, release_list)


request_polling = RequestPolling()
