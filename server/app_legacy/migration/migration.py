import json

from .migration_1_2 import migration_1_2_app, migration_5_6_hub


def migrate_dev(master_config_str: str) -> str:
    master_config = json.loads(master_config_str)
    dev_config = {}
    master_app_config_list: list[str] = master_config['app_config_list']
    app_config_list = []
    for master_app_config in master_app_config_list:
        master_app_config_str = __get_item_json_str(master_app_config)
        try:
            app_config_str = migration_1_2_app(master_app_config_str)
        except KeyError:
            app_config_str = None
        if app_config_str:
            app_config_list.append(json.loads(app_config_str))
    dev_config['app_config_list'] = app_config_list
    master_hub_config_list: list[str] = master_config['hub_config_list']
    hub_config_list = []
    for master_hub_config in master_hub_config_list:
        master_hub_config_str = __get_item_json_str(master_hub_config)
        try:
            hub_config_str = migration_5_6_hub(master_hub_config_str)
        except KeyError:
            hub_config_str = None
        if hub_config_str:
            hub_config_list.append(json.loads(hub_config_str))
    dev_config['hub_config_list'] = hub_config_list
    return json.dumps(dev_config, separators=(',', ':'))


def __get_item_json_str(item) -> str:
    if isinstance(item, dict):
        return json.dumps(item)
    else:
        return item
