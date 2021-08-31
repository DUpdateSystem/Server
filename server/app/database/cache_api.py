from time import time

from peewee import DoesNotExist

from app.database.model.hub_cache import HubCache
from app.database.model.memory_cache import MemoryCache
from app.database.model.release_cache import ReleaseCache
from .utils import to_json
from ..server.config import server_config
from ..server.manager.data.constant import logging

data_expire_sec = server_config.auto_refresh_time * 3600

if 6 * 3600 >= data_expire_sec >= 3 * 3600:
    memory_cache_expire_sec = int(data_expire_sec / 12)
else:
    memory_cache_expire_sec = 30 * 60


def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
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
    try:
        hub_info = HubCache.get((HubCache.hub_uuid == hub_uuid) & (HubCache.auth_str == to_json(auth)))
        release_cache_list = (ReleaseCache.select().where((ReleaseCache.hub_info == hub_info)
                                                          & (ReleaseCache.app_id_str == to_json(app_id))))
        if release_cache_list:
            release_cache = release_cache_list[0]
            release_cache.release = release
            release_cache.save()
            return
    except DoesNotExist:
        hub_info = HubCache(hub_uuid=hub_uuid, auth=auth)
        hub_info.save()
    ReleaseCache(hub_info=hub_info, app_id=app_id, release=release).save()


def get_memory_cache(key: str) -> str or None:
    timestamp = time() - memory_cache_expire_sec
    try:
        return MemoryCache.get((MemoryCache.key == key) & (MemoryCache.timestamp >= timestamp)).value
    except DoesNotExist:
        return None


def add_memory_cache(key: str, value: str):
    try:
        cache: MemoryCache = MemoryCache.get((MemoryCache.key == key))
        cache.value = value
        cache.update_timestamp()
    except DoesNotExist:
        MemoryCache(key=key, value=value).save()
