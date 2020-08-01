import json

from redis import BlockingConnectionPool
from redis.client import Redis

from app.config import server_config
from app.server.utils import logging
from .data.local_cache import local_cache

key_delimiter = '+'
value_dict_delimiter = ':'
release_cache_db_index = 0
tmp_cache_db_index = 1


class CacheManager:

    def __init__(self):
        self.__redis_release_cache_client = Redis(
            connection_pool=BlockingConnectionPool(host=server_config.redis_server_address,
                                                   port=server_config.redis_server_port,
                                                   password=server_config.redis_server_password,
                                                   db=release_cache_db_index))
        self.__redis_tmp_cache_client = Redis(
            connection_pool=BlockingConnectionPool(host=server_config.redis_server_address,
                                                   port=server_config.redis_server_port,
                                                   password=server_config.redis_server_password,
                                                   db=release_cache_db_index))

    def add_release_cache(self, hub_uuid: str, app_info: list, release_info: list or None = None):
        try:
            self.__add_release_cache(hub_uuid, app_info, release_info)
        except ConnectionError:
            pass

    def get_release_cache(self, hub_uuid: str, app_info: list) -> dict or None:
        try:
            return self.__get_release_cache(hub_uuid, app_info)
        except ConnectionError:
            pass

    def add_tmp_cache(self, key, value: str, ex_h: int = server_config.auto_refresh_time * 2):
        try:
            self.__add_tmp_cache(key, value, ex_h)
        except ConnectionError:
            pass

    def get_tmp_cache(self, key) -> str or None:
        try:
            return self.__get_tmp_cache(key)
        except ConnectionError:
            pass

    @staticmethod
    def __cache(redis_db: Redis, key: str, value: str, ex_h: int = None):
        if not server_config.use_cache_db:
            return
        if key:
            ex = None
            if ex_h:
                ex = ex_h * 3600
            redis_db.set(key, value, ex=ex)

    @staticmethod
    def __get(redis_db: Redis, key: str) -> str:
        if not server_config.use_cache_db or redis_db.exists(key) == 0:
            raise KeyError
        return redis_db.get(key)

    def __add_tmp_cache(self, key, value: str, ex_h: int = server_config.auto_refresh_time * 2):
        local_cache.add(key, value)
        self.__cache(self.__redis_tmp_cache_client, key, value, ex_h)

    def __get_tmp_cache(self, key) -> str:
        value = local_cache.get(key)
        if not value:
            value = self.__get(self.__redis_tmp_cache_client, key)
            local_cache.add(key, value)
        return value

    def __add_release_cache(self, hub_uuid: str, app_info: list, release_info: list or None = None):
        key = self.__get_app_cache_key(hub_uuid, app_info)
        value = json.dumps(release_info)
        self.__cache(self.__redis_release_cache_client, key, value, server_config.auto_refresh_time * 2)
        # 缓存完毕
        logging.debug(f"release caching: {app_info}")

    def __get_release_cache(self, hub_uuid: str, app_info: list) -> dict or None:
        key = self.__get_app_cache_key(hub_uuid, app_info)
        if key is None:
            logging.error(f"""WRONG FORMAT
hub_uuid: {hub_uuid}
app_info: {app_info}""", exc_info=server_config.debug_mode)
            raise NameError
        release_info = self.__get(self.__redis_release_cache_client, key)
        logging.debug(f"release cached: {app_info}")
        return json.loads(release_info)

    @property
    def cached_app_queue(self) -> dict:
        cache_app_info_dict = {}
        for key in self.__redis_release_cache_client.scan_iter():
            hub_uuid, app_info = self.__parsing_app_id(key.decode("utf-8"))
            app_info_list = []
            if hub_uuid in cache_app_info_dict:
                app_info_list = cache_app_info_dict[hub_uuid]
            app_info_list.append(app_info)
            cache_app_info_dict[hub_uuid] = app_info_list
        return cache_app_info_dict

    @staticmethod
    def __get_app_cache_key(hub_uuid: str, app_id: list) -> str or None:
        key = hub_uuid
        for k in app_id:
            try:
                key += (key_delimiter + k["key"] + value_dict_delimiter + k["value"])
            except TypeError:
                return None
        return key

    @staticmethod
    def __parsing_app_id(key: str) -> tuple:
        key_list = key.split(key_delimiter)
        hub_uuid = key_list[0]
        app_info = []
        for k in key_list[1:]:
            key, value = k.split(value_dict_delimiter, 1)
            app_info.append(
                {"key": key, "value": value}
            )
        return hub_uuid, app_info


cache_manager = CacheManager()
