import json

from proxy.format.header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST

start_index = 1
uuid_length = 36
second_index = start_index + uuid_length


def dump_release_request(hub_uuid: str, auth: dict, app_id: dict, use_cache: bool):
    body_json = json.dumps({
        'auth': auth,
        'app_id': app_id,
        'use_cache': use_cache,
    })
    return f'{RELEASE_REQUEST}{hub_uuid}{body_json}'


def load_release_request(request: str) -> tuple[str, dict, dict, bool]:
    hub_uuid = request[start_index: second_index]
    body_json = json.loads(request[second_index:])
    return hub_uuid, body_json['auth'], body_json['app_id'], body_json['use_cache']


def dump_download_request(hub_uuid: str, auth: dict, app_id: dict, asset_index: list):
    body_json = json.dumps({
        'auth': auth,
        'app_id': app_id,
        'asset_index': asset_index,
    })
    return f'{DOWNLOAD_REQUEST}{hub_uuid}{body_json}'


def load_download_request(request: str) -> tuple[str, dict, dict, list]:
    hub_uuid = request[start_index: second_index]
    body_json = json.loads(request[second_index:])
    return hub_uuid, body_json['auth'], body_json['app_id'], body_json['asset_index']


def dump_cloud_config_request(dev_version: bool, migrate_master: bool):
    body_json = json.dumps({
        'dev': dev_version,
        'migrate': migrate_master,
    })
    return f'{CLOUD_CONFIG_REQUEST}{body_json}'


def load_cloud_config_request(request: str) -> tuple[bool, bool]:
    body_json = json.loads(request[1:])
    return body_json['dev'], body_json['migrate']
