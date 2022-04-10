from time import time

from peewee import DoesNotExist

from config import auto_refresh_hour
from utils.logging import logging
from .model.hub_cache import HubCache
from .model.release_cache import ReleaseCache
from .model.temp_cache import TmpCache
from utils.json import to_json

data_expire_sec = auto_refresh_hour * 3600

if 6 * 3600 >= data_expire_sec >= 3 * 3600:
    memory_cache_expire_sec = int(data_expire_sec / 12)
else:
    memory_cache_expire_sec = 30 * 60


def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
    return __get_release_cache(hub_uuid, auth, app_id)


def __get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
    timestamp = time() - data_expire_sec
    release_cache_list: list[ReleaseCache] = (
        ReleaseCache.select(ReleaseCache).join(HubCache, on=(ReleaseCache.hub_info == HubCache.pair_id))
        # on 子句可以删除，因 peewee 自动推算
        # 参考: https://docs.peewee-orm.com/en/latest/peewee/relationships.html#performing-simple-joins
        .where((ReleaseCache.app_id_str == to_json(app_id))
               & (HubCache.hub_uuid == hub_uuid)
               & (HubCache.auth_str == to_json(auth))
               # 检查数据是否过期
               & (ReleaseCache.timestamp >= timestamp))
    )
    try:
        return release_cache_list[0].release
    except IndexError:
        logging.debug(f"no release cache: {hub_uuid}, {app_id}")
        return None


def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: list):
    return __add_release_cache(hub_uuid, auth, app_id, release)


def __add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: list):
    try:
        hub_info = HubCache.get((HubCache.hub_uuid == hub_uuid) & (HubCache.auth_str == to_json(auth)))
    except DoesNotExist:
        hub_info = HubCache.create(hub_uuid=hub_uuid, auth=auth)
    try:
        release_cache = (ReleaseCache.get((ReleaseCache.hub_info == hub_info)
                                          & (ReleaseCache.app_id_str == to_json(app_id))))
        release_cache.release = release
        release_cache.save()
    except DoesNotExist:
        ReleaseCache.create(hub_info=hub_info, app_id=app_id, release=release)


def get_memory_cache(key: str) -> bytes or None:
    return __get_memory_cache(key)


def __get_memory_cache(key: str) -> bytes or None:
    timestamp = time() - memory_cache_expire_sec
    try:
        return TmpCache.get((TmpCache.key == key) & (TmpCache.timestamp >= timestamp)).value
    except DoesNotExist:
        return None


def add_memory_cache(key: str, value: bytes):
    return __add_memory_cache(key, value)


def __add_memory_cache(key: str, value: bytes):
    try:
        cache: TmpCache = TmpCache.get((TmpCache.key == key))
        cache.value = value
        cache.update_timestamp()
        cache.save()
    except DoesNotExist:
        TmpCache.create(key=key, value=value)


def del_memory_cache(key: str):
    return __del_memory_cache(key)


def __del_memory_cache(key: str):
    try:
        TmpCache.get((TmpCache.key == key)).delete_instance()
    except DoesNotExist:
        pass
