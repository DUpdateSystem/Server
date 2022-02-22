import json
import time

from config import timeout_api
from proxy.format.header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST

start_index = 1
time_length = 19
second_index = start_index + time_length


def dump_release_request(hub_uuid: str, auth: dict, app_id: dict, use_cache: bool):
    body_json = json.dumps({
        'auth': auth,
        'app_id': app_id,
        'use_cache': use_cache,
        'hub_uuid': hub_uuid,
    })
    return f'{RELEASE_REQUEST}{get_localtime_str()}{body_json}'


def load_release_request(request: str) -> tuple[str, dict, dict, bool]:
    body_json = get_body_json(request)
    return body_json['hub_uuid'], body_json['auth'], body_json['app_id'], body_json['use_cache']


def dump_download_request(hub_uuid: str, auth: dict, app_id: dict, asset_index: list):
    body_json = json.dumps({
        'auth': auth,
        'app_id': app_id,
        'asset_index': asset_index,
        'hub_uuid': hub_uuid,
    })
    return f'{DOWNLOAD_REQUEST}{get_localtime_str()}{body_json}'


def load_download_request(request: str) -> tuple[str, dict, dict, list]:
    body_json = get_body_json(request)
    return body_json['hub_uuid'], body_json['auth'], body_json['app_id'], body_json['asset_index']


def dump_cloud_config_request(dev_version: bool, migrate_master: bool):
    body_json = json.dumps({
        'dev': dev_version,
        'migrate': migrate_master,
    })
    return f'{CLOUD_CONFIG_REQUEST}{get_localtime_str()}{body_json}'


def load_cloud_config_request(request: str) -> tuple[bool, bool]:
    body_json = json.loads(request[start_index:])
    return body_json['dev'], body_json['migrate']


time_temp = "%Y-%m-%d-%H:%M:%S"


def get_body_json(request: str):
    return json.loads(request[second_index:])


def get_localtime_str() -> str:
    return time.strftime(time_temp, time.localtime())


def dump_time_str_to_int(time_str: str) -> float:
    time_i = time.mktime(time.strptime(time_str, time_temp))
    return time_i


def check_time(request: str, timeout: int = timeout_api) -> bool:
    time_str = request[start_index:second_index]
    return dump_time_str_to_int(time_str) - time.time() <= timeout
