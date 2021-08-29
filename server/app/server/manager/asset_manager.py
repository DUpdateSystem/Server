import os
import pathlib
import time

import schedule

from app.migration.migration import migrate_dev
from app.server.config import server_config as _server_config
from app.server.manager.cache_manager import cache_manager
from app.server.utils.utils import get_response
from .data.constant import logging

_asset_dir_path = _server_config.download_asset_dir_path
_asset_dir_path.mkdir(parents=True, exist_ok=True)


def __mk_url(file_name: str) -> str:
    return f'http://{_server_config.download_asset_host}/download/{file_name}'


def write_byte_asset(file_name: str, byte_list):
    file_path = _asset_dir_path.joinpath(file_name)
    with open(file_path, "wb") as f:
        if byte_list is bytes:
            f.write(byte_list)
        else:
            for chunk in byte_list:
                f.write(chunk)
    return __mk_url(file_name)


def read_byte_asset(file_name: str) -> bytes:
    file_path = _asset_dir_path.joinpath(file_name)
    with open(file_path, "rb") as f:
        return f.read()


def __auto_clean_old_file():
    for (dir_path, _, filenames) in os.walk(_asset_dir_path):
        file = pathlib.PurePath(dir_path, filenames)
        ctime = os.path.getctime(file)
        current = time.time()
        if current - ctime >= 24 * 3600:
            os.remove(file)


schedule.every(_server_config.auto_refresh_time).hours.do(__auto_clean_old_file)


def get_cloud_config_str(dev_version: bool, migrate_master: bool) -> str or None:
    if dev_version and migrate_master:
        r_dev_version = False
    else:
        r_dev_version = dev_version
    cloud_config_str = _get_cloud_config_str(r_dev_version)
    if dev_version and migrate_master and cloud_config_str:
        cloud_config_str = migrate_dev(cloud_config_str)
    return cloud_config_str


def _get_cloud_config_str(dev_version: bool) -> str or None:
    if dev_version:
        cache_key = "cloud_config_dev"
    else:
        cache_key = "cloud_config"
    try:
        cache_str = cache_manager.get_tmp_cache(cache_key)
    except KeyError:
        cache_str = None
    if cache_str:
        logging.info("Cloud Config: 命中缓存")
        return cache_str
    else:
        logging.info("Cloud Config: 未缓存")
        cloud_config_str = __get_cloud_config_str(dev_version, True)
        if cloud_config_str:
            logging.info("Cloud Config: 配置获取成功")
            cache_manager.add_tmp_cache(cache_key, cloud_config_str)
            return cloud_config_str
        else:
            logging.info(f"Cloud Config: 配置获取失败（dev: {dev_version}）")


def __get_cloud_config_str(dev_version: bool, use_self_worker: bool = True) -> str or None:
    if dev_version:
        rule_hub_url = "https://raw.githubusercontent.com/DUpdateSystem/UpgradeAll-rules/" \
                       "dev/rules/rules.json"
    else:
        rule_hub_url = _server_config.cloud_rule_hub_url
    back = rule_hub_url
    if use_self_worker:
        rule_hub_url = "https://re.flaw.workers.dev/" + rule_hub_url
    response = get_response(rule_hub_url)
    if response:
        return response.text
    else:
        response = get_response(back)
        return response
