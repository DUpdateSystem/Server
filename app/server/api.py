from app.server.hubs.hub_list import hub_dict
from .manager.data_manager import data_manager
from .utils import logging


def get_app_status(hub_uuid: str, app_id: list,
                   fun_id: int = 0, http_response: dict = None,
                   use_cache=True, cache_data=True) -> dict or None:
    if hub_uuid not in hub_dict:
        logging.warning(f"NO HUB: {hub_uuid}")
        return None
    if fun_id:
        logging.info(f"分步函数运行{fun_id}: hub_uuid: {hub_uuid} app_id: {app_id}")
    app_status = data_manager.get_app_status(hub_uuid, app_id, use_proxy=True,
                                             fun_id=fun_id, http_response=http_response,
                                             use_cache=use_cache, cache_data=cache_data)
    if 'http_proxy' in app_status:
        logging.info(f"请求客户端代理: hub_uuid: {hub_uuid} app_id: {app_id}")
    else:
        log_str = ""
        if not app_status['app_status']['release_info']:
            log_str += "(empty)"
        logging.info(f"已完成单个请求: hub_uuid: {hub_uuid} app_id: {app_id}{log_str}")
    return app_status


def get_download_info(hub_uuid: str, app_id: list,
                      asset_index: list) -> dict or None:
    logging.info(f"请求下载资源: hub_uuid: {hub_uuid} app_id: {app_id}")
    download_info = data_manager.get_download_info(hub_uuid, app_id,
                                                   asset_index)
    logging.info(f"回应下载资源: download_info: {download_info}")
    return download_info
