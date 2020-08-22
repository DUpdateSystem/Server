from .manager.data_manager import data_manager
from .utils import logging


def get_release_dict(hub_uuid: str, auth: dict, app_id_list: list,
                     use_cache=True, cache_data=True) -> dict or None:
    release_dict = data_manager.get_release_dict(hub_uuid, app_id_list, auth=auth,
                                                 use_cache=use_cache, cache_data=cache_data)
    if not release_dict:
        return {"valid_hub_uuid": False}
    release_package_list = [{"app_id": app_id, "release_list": release_dict[app_id]} for app_id in release_dict]
    return {
        "valid_hub_uuid": True,
        "release_package_list": release_package_list
    }


def get_download_info(hub_uuid: str, app_id: list,
                      asset_index: list) -> dict or None:
    logging.info(f"请求下载资源: hub_uuid: {hub_uuid} app_id: {app_id}")
    download_info = data_manager.get_download_info(hub_uuid, app_id,
                                                   asset_index)
    logging.info(f"回应下载资源: download_info: {download_info}")
    return download_info
