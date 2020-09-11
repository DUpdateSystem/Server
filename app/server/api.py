from .manager.data.constant import logging
from .manager.data_manager import data_manager
from .utils import dict_to_grcp_dict_list


def init_account(hub_uuid: str, account: dict) -> dict:
    auth = data_manager.init_account(hub_uuid, account)
    return {"auth": dict_to_grcp_dict_list(auth)}


def get_release_dict(hub_uuid: str, auth: dict or None, app_id_list: list,
                     use_cache=True, cache_data=True) -> dict:
    iter_fun = data_manager.get_release(hub_uuid, app_id_list, auth=auth,
                                        use_cache=use_cache, cache_data=cache_data)
    if iter_fun is None:
        yield {"valid_hub": False}
    for item in iter_fun:
        app_id = item["app_id"]
        release_list = item["release_list"]
        release_package = {
            "app_id": dict_to_grcp_dict_list(app_id)
        }
        if release_list and release_list[0] is None:
            release_package["valid_data"] = False
        else:
            release_package["valid_data"] = True
            release_package["release_list"] = release_list
        yield {
            "valid_hub": True,
            "release": release_package
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
