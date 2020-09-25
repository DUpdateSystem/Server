import json
from time import time

from rediscluster import RedisCluster

from app.server.config import server_config
from .data.constant import logging
from .data.local_cache import local_cache

key_delimiter = '+'
value_dict_delimiter = ':'
release_cache_db_index = 0
tmp_cache_db_index = 1

redis_renew_time_set_key = "renew_time"

startup_nodes = [{"host": server_config.redis_server_address, "port": server_config.redis_server_port}]


class CacheManager:

    def __init__(self):
        self.__redis_release_cache_client = \
            self.__redis_tmp_cache_client = RedisCluster(startup_nodes=startup_nodes,
                                                         decode_responses=True,
                                                         password=server_config.redis_server_password)

    def add_release_cache(self, hub_uuid: str, app_id: dict, release_info: list or None = None):
        try:
            self.__add_release_cache(hub_uuid, app_id, release_info)
        except ConnectionError:
            pass

    def get_release_cache(self, hub_uuid: str, app_id: dict) -> dict or None:
        try:
            return self.__get_release_cache(hub_uuid, app_id)
        except ConnectionError:
            pass

    def del_release_cache(self, key: str):
        try:
            self.__redis_release_cache_client.delete(key)
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
    def __cache(redis_db: RedisCluster, key: str, value: str, ex_h: int = None):
        if not server_config.use_cache_db:
            return
        if key:
            ex = None
            if ex_h:
                ex = ex_h * 3600
            redis_db.set(key, value, ex=ex)
            redis_db.zadd(redis_renew_time_set_key, {key: int(time() / 60)}, incr=True)

    @staticmethod
    def __get(redis_db: RedisCluster, key: str) -> str:
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

    def __add_release_cache(self, hub_uuid: str, app_id: dict, release_info: list or None = None):
        key = self.__get_app_cache_key(hub_uuid, app_id)
        value = json.dumps(release_info)
        self.__cache(self.__redis_release_cache_client, key, value, server_config.auto_refresh_time * 4)
        # 缓存完毕
        logging.debug(f"release caching: {key}")

    def __get_release_cache(self, hub_uuid: str, app_id: dict) -> dict or None:
        key = self.__get_app_cache_key(hub_uuid, app_id)
        if key is None:
            logging.error(f"""WRONG FORMAT
hub_uuid: {hub_uuid}
app_id: {app_id}""", exc_info=server_config.debug_mode)
            raise NameError
        release_info = self.__get(self.__redis_release_cache_client, key)
        logging.debug(f"release cached: {key}")
        return json.loads(release_info)

    @property
    def cached_app_queue(self) -> dict:
        cache_app_id_dict = {}
        key_list = self.__redis_tmp_cache_client.zrangebyscore(redis_renew_time_set_key, -1,
                                                               int(time() / 60) - server_config.auto_refresh_time * 60)
        for key in key_list:
            # noinspection PyBroadException
            try:
                hub_uuid, app_id = self.__parsing_app_id(key.decode("utf-8"))
                app_id_list = []
                if hub_uuid in cache_app_id_dict:
                    app_id_list = cache_app_id_dict.get(hub_uuid)
                app_id_list.append(app_id)
                cache_app_id_dict[hub_uuid] = app_id_list
            except Exception:
                self.del_release_cache(key)
        return cache_app_id_dict

    @staticmethod
    def __get_app_cache_key(hub_uuid: str, app_id: dict) -> str or None:
        key = hub_uuid
        for k in app_id:
            try:
                key += (key_delimiter + k + value_dict_delimiter + app_id[k])
            except TypeError:
                return None
        return key

    @staticmethod
    def __parsing_app_id(key: str) -> tuple:
        key_list = key.split(key_delimiter)
        hub_uuid = key_list[0]
        app_id = {}
        for k in key_list[1:]:
            key, value = k.split(value_dict_delimiter, 1)
            app_id[key] = value
        return hub_uuid, app_id


cache_manager = CacheManager()
