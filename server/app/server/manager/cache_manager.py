import functools
import json
from time import time

from redis import ConnectionPool, Redis
from rediscluster import RedisCluster
from rediscluster.exceptions import RedisClusterException

from app.server.config import server_config
from app.status_checker.status import set_redis_availability, get_redis_availability
from .data.constant import logging
from .data.local_cache import local_cache

key_delimiter = '+'
value_dict_delimiter = ':'
release_cache_db_index = 0
tmp_cache_db_index = 1

auto_renew_queue_size = 500
redis_renew_time_set_key = "renew_time"

startup_nodes = server_config.redis_node_list


class CacheManager:

    def __init__(self):
        self.__redis_client = None

    @property
    def __redis_release_cache_client(self):
        # noinspection PyBroadException
        try:
            redis_client = self.__get_redis_client()
            set_redis_availability(True)
            return redis_client
        except Exception as e:
            set_redis_availability(False)
            raise e

    @property
    def __redis_tmp_cache_client(self):
        return self.__redis_release_cache_client

    def __get_redis_client(self) -> RedisCluster:
        if not self.__redis_client:
            if len(startup_nodes) > 1:
                self.__redis_client = RedisCluster(startup_nodes=startup_nodes,
                                                   decode_responses=False,
                                                   password=server_config.redis_server_password)
            else:
                node = startup_nodes[0]
                host = node["host"]
                port = node["port"]
                pool = ConnectionPool(host=host, port=port,
                                      password=server_config.redis_server_password,
                                      db=release_cache_db_index)
                self.__redis_client = Redis(connection_pool=pool, socket_timeout=15, socket_connect_timeout=15)
        return self.__redis_client

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

    @functools.lru_cache(maxsize=16)
    def get_tmp_cache(self, key) -> str or None:
        try:
            return self.__get_tmp_cache(key)
        except ConnectionError:
            pass

    def __set(self, redis_db: RedisCluster, key: str, value: str, ex_h: int = None):
        if not get_redis_availability():
            return
        # noinspection PyBroadException
        try:
            self.__set0(redis_db, key, value, ex_h)
            set_redis_availability(True)
        except Exception:
            set_redis_availability(False)

    @staticmethod
    def __set0(redis_db: RedisCluster, key: str, value: str, ex_h: int = None):
        if not server_config.use_cache_db:
            return
        key = key.encode('utf-8').strip()
        if key:
            ex = None
            if ex_h:
                ex = ex_h * 3600
            redis_db.set(key, value, ex=ex)
            redis_db.zrem(redis_renew_time_set_key, key)
            redis_db.zadd(redis_renew_time_set_key, {key: int(time() / 60)})

    def __get(self, redis_db: RedisCluster, key: str) -> str:
        if not get_redis_availability():
            raise RedisClusterException()
        # noinspection PyBroadException
        try:
            value = self.__get0(redis_db, key)
            set_redis_availability(True)
            return value
        except KeyError as e:
            raise e
        except Exception as e:
            set_redis_availability(False)
            raise e

    @staticmethod
    def __get0(redis_db: RedisCluster, key: str) -> str:
        key = key.encode('utf-8').strip()
        if not server_config.use_cache_db or redis_db.exists(key) == 0:
            raise KeyError
        return redis_db.get(key)

    def __add_tmp_cache(self, key, value: str, ex_h: int = server_config.auto_refresh_time * 2):
        local_cache.add(key, value)
        self.__set(self.__redis_tmp_cache_client, key, value, ex_h)

    def __get_tmp_cache(self, key) -> str:
        value = local_cache.get(key)
        if not value:
            value = self.__get(self.__redis_tmp_cache_client, key)
            local_cache.add(key, value)
        return value

    def __add_release_cache(self, hub_uuid: str, app_id: dict, release_info: list or None = None):
        key = self.__get_app_cache_key(hub_uuid, app_id)
        value = json.dumps(release_info)
        self.__set(self.__redis_release_cache_client, key, value, server_config.auto_refresh_time * 4)
        # 缓存完毕
        logging.debug(f"release caching: {key}")

    def __get_release_cache(self, hub_uuid: str, app_id: dict) -> dict or None:
        key = self.__get_app_cache_key(hub_uuid, app_id)
        if key is None:
            logging.error(f"""WRONG FORMAT
hub_uuid: {hub_uuid}
app_id: {app_id}""", exc_info=server_config.debug_mode)
            raise NameError
        release_info = self.__get_release_cache_value(key)
        if release_info:
            return json.loads(release_info)
        else:
            return release_info

    def __get_release_cache_value(self, key):
        # noinspection PyBroadException
        try:
            value = self.__get_release_cache_cache_core(key)
            logging.debug(f"release cached: {key}")
            return value
        except Exception:
            pass

    @functools.lru_cache(maxsize=512)
    def __get_release_cache_cache_core(self, key):
        return self.__get(self.__redis_release_cache_client, key)

    @property
    def cached_app_queue(self) -> dict:
        cache_app_id_dict = {}
        key_list = self.__redis_tmp_cache_client.zrangebyscore(redis_renew_time_set_key, '-inf',
                                                               int(time() / 60) - server_config.auto_refresh_time * 60)
        for key in key_list[:auto_renew_queue_size]:
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
