from .callback_map import call_callback
from .header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST


def get_release_key(hub_uuid: str, auth: dict, app_id: dict, use_cache: bool):
    return f"{RELEASE_REQUEST}{hub_uuid}{auth}{app_id}{use_cache}"


def get_download_key(hub_uuid: str, auth: dict, app_id: list, asset_index: list):
    return f"{DOWNLOAD_REQUEST}{hub_uuid}{auth}{app_id}{asset_index}"


def get_cloud_config_key(dev_version: bool, migrate_master: bool):
    return f"{CLOUD_CONFIG_REQUEST}{dev_version}{migrate_master}"


def respond_release(hub_uuid: str, auth: dict, app_id: dict, use_cache: bool, release_list):
    key = get_release_key(hub_uuid, auth, app_id, use_cache)
    call_callback(key, release_list)


def respond_download(hub_uuid: str, auth: dict, app_id: list, asset_index: list, download_info):
    key = get_download_key(hub_uuid, auth, app_id, asset_index)
    call_callback(key, download_info)


def respond_cloud_config(dev_version: bool, migrate_master: bool, cloud_config):
    key = get_cloud_config_key(dev_version, migrate_master)
    call_callback(key, cloud_config)
