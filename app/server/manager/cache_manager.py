import json

from redis import BlockingConnectionPool
from redis.client import Redis

from app.config import logging
from app.config import server_config

key_delimiter = '+'
value_dict_delimiter = ':'
release_cache_db_index = 0


class CacheManager:

    def __init__(self):
        self.__redis_release_cache_client = Redis(
            connection_pool=BlockingConnectionPool(host=server_config.redis_server_address,
                                                   port=server_config.redis_server_port,
                                                   db=release_cache_db_index))

    def add_release_cache(self, hub_uuid: str, app_info: list, release_info: list or None = None):
        key = self.__get_app_cache_key(hub_uuid, app_info)
        if key is not None:
            ex_h = server_config.auto_refresh_time + 4
            self.__redis_release_cache_client.set(key, json.dumps(release_info),
                                                  ex=ex_h * 3600)
            # 缓存完毕
            logging.debug(f"release caching: {app_info}")

    def get_release_cache(self, hub_uuid: str, app_info: list) -> dict or None:
        key = self.__get_app_cache_key(hub_uuid, app_info)
        if key is None:
            logging.error(f"""WRONG FORMAT
hub_uuid: {hub_uuid}
app_info: {app_info}""")
            raise NameError
        if self.__redis_release_cache_client.exists(key) == 0:
            raise KeyError
        release_info = self.__redis_release_cache_client.get(key)
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
        if not app_id:
            return None
        key = hub_uuid
        for k in app_id:
            key += (key_delimiter + k["key"] + value_dict_delimiter + k["value"])
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
