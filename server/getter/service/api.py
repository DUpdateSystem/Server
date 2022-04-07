from getter.api.cloud_config_getter import get_cloud_config_str as _get_cloud_config_str
from getter.api.download_getter import get_download_info_list as _get_download_info_list
from getter.api.release_getter import get_single_release as _get_single_release
from .cache import get_tmp_cache_or_run, get_re_cache_or_run


def get_cloud_config_str(dev_version: bool, migrate_master: bool) -> str or None:
    if dev_version:
        cache_key = "cloud_config_dev"
    else:
        cache_key = "cloud_config"
    return get_tmp_cache_or_run(cache_key, _get_cloud_config_str, dev_version, migrate_master)


def get_single_release(hub_uuid: str, auth: dict or None, app_id: dict, use_cache=True) -> list or None:
    if not use_cache:
        return _get_single_release(hub_uuid, auth, app_id)
    return get_re_cache_or_run(hub_uuid, auth, app_id, _get_single_release)


def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
    return _get_download_info_list(hub_uuid, auth, app_id, asset_index)
