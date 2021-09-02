from .manager.data.constant import logging
from .manager.data_manager import data_manager


def init_account(hub_uuid: str, account: dict) -> dict:
    auth = data_manager.init_account(hub_uuid, account)
    return {"auth": auth}


def get_release_dict(hub_uuid: str, auth: dict or None, app_id: dict,
                     use_cache=True, cache_data=True) -> dict:
    try:
        release_list = data_manager.get_single_release(hub_uuid, auth, app_id, use_cache=use_cache)
    except KeyError:
        return {"valid_hub": False}
    release_package = {}
    if release_list and release_list[0] is None:
        release_package["valid_data"] = False
    else:
        release_package["valid_data"] = True
        release_package["release_list"] = release_list
    yield {"release": release_package}


def get_download_info_list(hub_uuid: str, auth: dict, app_id: dict,
                           asset_index: list) -> dict:
    logging.info(f"请求下载地址: hub_uuid: {hub_uuid} app_id: {app_id}")
    download_info_list = data_manager.get_download_info_list(hub_uuid, auth, app_id, asset_index)
    logging.info(f"回应下载资源: {download_info_list}")
    return download_info_list
