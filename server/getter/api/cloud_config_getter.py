from config import cloud_rule_hub_url
from utils.logging import logging
from utils.requests import get_response
from .cloud_config_migration.migration import migrate_dev


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
    cloud_config_str = __get_cloud_config_str(dev_version, True)
    if cloud_config_str:
        logging.info("Cloud Config: 配置获取成功")
    else:
        logging.info(f"Cloud Config: 配置获取失败（dev: {dev_version}）")
    return cloud_config_str


def __get_cloud_config_str(dev_version: bool, use_self_worker: bool = True) -> str or None:
    if dev_version:
        rule_hub_url = "https://raw.githubusercontent.com/DUpdateSystem/UpgradeAll-rules/" \
                       "dev/rules/rules.json"
    else:
        rule_hub_url = cloud_rule_hub_url
    back = rule_hub_url
    if use_self_worker:
        rule_hub_url = "https://re.flaw.workers.dev/" + rule_hub_url
    response = get_response(rule_hub_url)
    if response:
        return response.text
    else:
        response = get_response(back)
        return response
