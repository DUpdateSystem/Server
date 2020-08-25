from .manager.data_manager import data_manager
from .utils import logging, dict_to_grcp_dict_list


def init_account(hub_uuid: str, account: dict) -> dict:
    auth = data_manager.init_account(hub_uuid, account)
    return {"auth": dict_to_grcp_dict_list(auth)}


def get_release_dict(hub_uuid: str, auth: dict or None, app_id_list: list,
                     use_cache=True, cache_data=True) -> dict:
    app_id_index = {frozenset(app_id): app_id for app_id in app_id_list}
    release_dict = data_manager.get_release_dict(hub_uuid, app_id_list, auth=auth,
                                                 use_cache=use_cache, cache_data=cache_data)
    if not release_dict:
        return {"valid_hub_uuid": False}
    release_package_list = [{"app_id": app_id_index[f_app_id], "release_list": release_dict[f_app_id]}
                            for f_app_id in release_dict]
    return {
        "valid_hub_uuid": True,
        "release_package_list": release_package_list
    }


def get_download_info(hub_uuid: str, auth: dict, app_id: dict,
                      asset_index: list) -> dict:
    logging.info(f"请求下载地址: hub_uuid: {hub_uuid} app_id: {app_id}")
    download_info_list = data_manager.get_download_info(hub_uuid, auth, app_id, asset_index)
    download_info_dict = {}
    if download_info_list:
        download_package_list = []
        for download_info in download_info_list:
            download_package = {'url': download_info[0]}
            if len(download_info) > 1:
                download_package['request_header'] = dict_to_grcp_dict_list(download_info[1])
            download_package_list.append(
                download_package
            )
        download_info_dict = {'list': download_package_list}
    logging.info(f"回应下载资源: download_info: {download_info_dict}")
    return download_info_dict


def download_file(url: str, auth: dict) -> dict:
    logging.info(f"请求下载资源: url: {url} auth: {auth}")
    download_file_byte_dict = data_manager.download_file(url, auth)
    logging.info(f"回应下载资源: download_info: {download_file_byte_dict}")
    return download_file_byte_dict
