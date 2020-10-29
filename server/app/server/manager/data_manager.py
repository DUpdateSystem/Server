import asyncio
from datetime import timedelta
from threading import Thread

from app.server.config import server_config
from app.server.hubs.hub_list import hub_dict
from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import logging, time_loop
from app.server.manager.data.generator_cache import GeneratorCache
from app.server.utils import run_fun_list


class DataManager:

    @staticmethod
    def init_account(hub_uuid: str, account: dict) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
        # noinspection PyBroadException
        try:
            return hub.init_account(account)
        except Exception:
            logging.error(f"""hub_uuid: {hub_uuid} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    def get_release(self, hub_uuid: str, app_id_list: list, auth: dict or None = None,
                    use_cache=True, cache_data=True) -> dict or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        return self.__get_release(hub_uuid, app_id_list, auth, use_cache, cache_data)

    @staticmethod
    def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return None
        hub = hub_dict[hub_uuid]
        # noinspection PyBroadException
        try:
            download_info = hub.get_download_info(app_id, asset_index, auth)
            if type(download_info) is str:
                return [{"url": download_info}]
            else:
                return download_info
        except Exception:
            logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
            return None

    def refresh_cache(self):
        i = 0
        logging.info("refresh all data: start")
        cache_queue = cache_manager.cached_app_queue
        for hub_uuid in cache_queue.keys():
            release_iter = self.get_release(hub_uuid, cache_queue[hub_uuid], use_cache=False)
            if release_iter:
                for _ in release_iter:
                    i += 1
        logging.info(f"refresh all data: finish({i})")

    @staticmethod
    def __get_release_cache(hub_uuid: str, app_id: dict) -> dict or None:
        try:
            return cache_manager.get_release_cache(hub_uuid, app_id)
        except (KeyError, NameError):
            pass

    def __get_release(self, hub_uuid: str, app_id_list: list, auth: dict or None = None,
                      use_cache=True, cache_data=True) -> dict or None:
        nocache = []
        if use_cache:
            release_list_iter, thread = self.__get_release_cache_iter(hub_uuid, app_id_list)
            for app_id, release_list in release_list_iter:
                if release_list and not (len(release_list) == 1 and release_list[0] is None):
                    yield {"app_id": app_id, "release_list": release_list}
                else:
                    nocache.append(app_id)
            thread.join()
        else:
            nocache = app_id_list
        if nocache:
            generator_cache, thread = self.__get_release_nocache(hub_uuid, nocache, auth)
            for item in generator_cache:
                app_id = item["id"]
                release_list = item["v"]
                if cache_data:
                    if release_list is not None:
                        cache_manager.add_release_cache(hub_uuid, app_id, release_list)
                yield {"app_id": app_id, "release_list": release_list}
            thread.join()

    def __get_release_cache_iter(self, hub_uuid: str, app_id_list: list) -> tuple:
        generator_cache = GeneratorCache()
        thread = Thread(target=run_fun_list,
                        args=([lambda: asyncio.run(
                            self.__get_release_cache_async(generator_cache, hub_uuid, app_id_list),
                            debug=server_config.debug_mode),
                               generator_cache.close],))
        thread.start()
        return generator_cache, thread

    async def __get_release_cache_async(self, generator_cache: GeneratorCache,
                                        hub_uuid: str, app_id_list: list):
        core_list = [self.__get_release_cache_async0(generator_cache, hub_uuid, app_id) for app_id in app_id_list]
        await asyncio.gather(*core_list)

    async def __get_release_cache_async0(self, generator_cache: GeneratorCache,
                                         hub_uuid: str, app_id: dict):
        generator_cache.add_value((app_id, self.__get_release_cache(hub_uuid, app_id)))

    def __get_release_nocache(self, hub_uuid: str, app_id_list: list, auth: dict or None = None) -> tuple:
        generator_cache = GeneratorCache()
        hub = hub_dict[hub_uuid]
        if len(app_id_list) > 5:
            timeout = len(app_id_list) * 11.25
        else:
            timeout = 30
        thread = Thread(target=run_fun_list,
                        args=([lambda: asyncio.run(
                            self.__run_get_release_fun(hub, generator_cache, timeout, app_id_list, auth),
                            debug=server_config.debug_mode),
                               generator_cache.close],))
        thread.start()
        return generator_cache, thread

    async def __run_get_release_fun(self, hub, generator_cache: GeneratorCache, timeout: int, app_id_list: list,
                                    auth: dict or None = None):
        hub_core = hub.get_release_list(generator_cache, app_id_list, auth)
        await self.__run_core(hub_core, timeout)

    @staticmethod
    async def __run_core(aw, timeout):
        try:
            await asyncio.wait_for(aw, timeout=timeout)
        except asyncio.TimeoutError:
            print(f'aw: {aw} timeout!')


data_manager = DataManager()


@time_loop.job(interval=timedelta(hours=server_config.auto_refresh_time))
def _auto_refresh():
    logging.info("auto refresh data: start")
    data_manager.refresh_cache()
    logging.info("auto refresh data: finish")
