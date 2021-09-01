from app.server.request_processor.queue.callback_map import add_callback
from app.server.request_processor.queue.request_getter import request_list
from app.server.request_processor.queue.respond_sender import get_release_key, get_download_key, get_cloud_config_key


def get_release_list(hub_uuid: str, auth: dict, app_id: dict, use_cache: bool, callback):
    key = get_release_key(hub_uuid, auth, app_id, use_cache)
    add_callback(key, callback)
    request_list.add_releases_request(hub_uuid, auth, app_id, use_cache)


def get_download(hub_uuid: str, auth: dict, app_id: list, asset_index: list, callback):
    key = get_download_key(hub_uuid, auth, app_id, asset_index)
    add_callback(key, callback)
    request_list.add_download_request(hub_uuid, auth, app_id, asset_index)


def get_cloud_config(dev_version: bool, migrate_master: bool, callback):
    key = get_cloud_config_key(dev_version, migrate_master)
    add_callback(key, callback)
    request_list.add_cloud_config_request(dev_version, migrate_master)
