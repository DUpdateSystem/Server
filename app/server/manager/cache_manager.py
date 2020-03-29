import json
from redis.client import Redis
from redis import BlockingConnectionPool
from app.main import config

key_delimiter = '+'
value_dict_delimiter = ':'
cache_db_index = 0


class CacheManager:

    def __init__(self):
        self.___redis_client = Redis(
            connection_pool=BlockingConnectionPool(host=config.redis_server_address, port=config.redis_server_port,
                                                   db=cache_db_index))

    @staticmethod
    def __get_app_info_key(hub_uuid: str, app_info: list) -> str or None:
        if not app_info:
            return None
        key = hub_uuid
        for k in app_info:
            key += (key_delimiter + k.get('key') + value_dict_delimiter + k.get('value'))
        return key

    @staticmethod
    def __parsing_app_info(key: str) -> tuple:
        key_list = key.split(key_delimiter)
        hub_uuid = key_list[0]
        app_info = []
        for k in key_list[1:]:
            key, value = k.split(value_dict_delimiter)
            app_info.append({
                'key': key,
                'value': value
            })
        return hub_uuid, app_info

    def add_to_cache_queue(self, hub_uuid: str, app_info: list, release_info: list or None = None):
        key = self.__get_app_info_key(hub_uuid, app_info)
        if key is not None:
            self.___redis_client.set(key, json.dumps(release_info))
            # 缓存完毕
            print(f"cache {app_info}.")

    def get_cache(self, hub_uuid: str, app_info: list) -> dict or None:
        key = self.__get_app_info_key(hub_uuid, app_info)
        if key is not None:
            release_info = self.___redis_client.get(key)
            if release_info is not None:
                print(str(app_info) + " is cached.")
                return json.loads(release_info)
        return None

    @property
    def cache_queue(self) -> dict:
        cache_app_info_dict = {}
        for key in self.___redis_client.scan_iter():
            hub_uuid, app_info = self.__parsing_app_info(key)
            app_info_list = []
            if hub_uuid in cache_app_info_dict:
                app_info_list = cache_app_info_dict[hub_uuid]
            app_info_list.append(app_info)
            cache_app_info_dict[hub_uuid] = app_info_list
        return cache_app_info_dict
