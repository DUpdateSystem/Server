import asyncio
from multiprocessing import Process, Event
from threading import Thread

from app.server.manager.cache_manager import cache_manager
from app.server.utils.queue import LightQueue
from app.server.utils.utils import set_new_asyncio_loop, call_fun_in_loop
from .getter.cloud_config_getter import get_cloud_config_str
from .getter.download_getter import get_download_info_list
from .getter.release_getter import get_release
from .queue.request_getter import request_list, CLOUD_CONFIG_REQUEST, RELEASE_REQUEST, DOWNLOAD_REQUEST
from .queue.respond_sender import respond_release, respond_download, respond_cloud_config


class RequestPolling:
    process: Process or None = None

    def start(self) -> Process:
        if not self.process:
            self.process = Process(target=self._run_getter, daemon=True)
            self.process.start()
        return self.process

    def join(self, timeout=None):
        if self.process:
            self.process.join(timeout)

    def kill(self):
        self.process.kill()

    def stop(self):
        request_list.close()

    @staticmethod
    async def get_download_info(hub_uuid: str, auth: dict, app_id: list, asset_index: list):
        download_info = await get_download_info_list(hub_uuid, auth, app_id, asset_index)
        respond_download(hub_uuid, auth, app_id, asset_index, download_info)

    @staticmethod
    async def get_release(hub_uuid: str, auth: dict or None, app_id: dict,
                          use_cache=True, cache_data=True):
        release_list = await get_release(hub_uuid, auth, app_id, use_cache, cache_data)
        respond_release(hub_uuid, auth, app_id, use_cache, release_list)

    @staticmethod
    async def get_cloud_config(dev_version: bool, migrate_master: bool):
        cloud_config = get_cloud_config_str(dev_version, migrate_master)
        respond_cloud_config(dev_version, migrate_master, cloud_config)

    async def __get_request(self, queue: LightQueue):
        cache_manager.connect()
        async for key, args in queue:
            if key == CLOUD_CONFIG_REQUEST:
                asyncio.create_task(self.get_cloud_config(*args))
            elif key == RELEASE_REQUEST:
                asyncio.create_task(self.get_release(*args))
            elif key == DOWNLOAD_REQUEST:
                asyncio.create_task(self.get_download_info(*args))
        cache_manager.disconnect()

    def __start_queue_convert(self, loop) -> LightQueue:
        queue = LightQueue(loop=loop)
        Thread(target=self._queue_converter, args=(loop, queue)).start()
        return queue

    @staticmethod
    def _queue_converter(loop, queue: LightQueue):
        for item in request_list:
            call_fun_in_loop(queue.put(item), loop)

    def _run_getter(self):
        loop = set_new_asyncio_loop()
        request_queue = self.__start_queue_convert(loop)
        loop.run_until_complete(self.__get_request(request_queue))
        loop.close()


request_polling = RequestPolling()
