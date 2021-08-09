from .manager.data.constant import logging
from .manager.data_manager import data_manager
from .utils.utils import dict_to_grcp_dict_list


def init_account(hub_uuid: str, account: dict) -> dict:
    auth = data_manager.init_account(hub_uuid, account)
    return {"auth": dict_to_grcp_dict_list(auth)}


def get_release_dict(hub_uuid: str, auth: dict or None, app_id_list: list,
                     use_cache=True, cache_data=True) -> dict:
    iter_fun = data_manager.get_release(hub_uuid, app_id_list, auth=auth,
                                        use_cache=use_cache)
    if iter_fun is None:
        return {"valid_hub": False}
    else:
        yield {"valid_hub": True}
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
        yield {"release": release_package}


def get_download_info_list(hub_uuid: str, auth: dict, app_id: dict,
                           asset_index: list) -> dict:
    logging.info(f"请求下载地址: hub_uuid: {hub_uuid} app_id: {app_id}")
    download_info_list = data_manager.get_download_info_list(hub_uuid, auth, app_id, asset_index)
    log_text = ""
    if not download_info_list:
        download_info_dict = {}
        log_text += "None"
    else:
        download_info_dict = {'list': [{
            "url": download_item["url"],
            "name": download_item.get("name"),
            "headers": dict_to_grcp_dict_list(download_item.get("headers")),
            "cookies": dict_to_grcp_dict_list(download_item.get("cookies")),
        } for download_item in download_info_list]}
        log_text += f"list: url: {len(download_info_dict['list'])}," \
                    f" headers: {len(download_info_dict['list'][0]['headers'])}," \
                    f" cookies: {len(download_info_dict['list'][0]['cookies'])}"
    logging.info(f"回应下载资源: {log_text}")
    return download_info_dict


def get_download_info(hub_uuid: str, auth: dict, app_id: dict,
                      asset_index: list) -> dict:
    download_info_dict = get_download_info_list(hub_uuid, auth, app_id, asset_index)
    if 'list' in download_info_dict:
        return {'url': download_info_dict['list'][0].get('url')}
    else:
        return download_info_dict
