from peewee import DoesNotExist

from .hub_cache import HubCache
from .release_cache import ReleaseCache
from .utils import to_json
from ..server.manager.data.constant import logging


def get_release_cache(hub_uuid: str, auth: dict or None, app_id: dict) -> dict or None:
    release_cache_list: list[ReleaseCache] = (
        ReleaseCache.select(ReleaseCache).join(HubCache, on=(ReleaseCache.hub_info == HubCache.pair_id))
        # on 子句可以删除，因 peewee 自动推算
        # 参考: https://docs.peewee-orm.com/en/latest/peewee/relationships.html#performing-simple-joins
        .where((ReleaseCache.app_id_str == to_json(app_id))
               & (HubCache.hub_uuid == hub_uuid)
               & (HubCache.auth_str == to_json(auth))))
    try:
        return release_cache_list[0].release
    except IndexError:
        logging.debug(f"no release cache: {hub_uuid}, {app_id}")
        return None


def add_release_cache(hub_uuid: str, auth: dict or None, app_id: dict, release: dict):
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
