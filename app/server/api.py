from .hubs.library.hub_list import hub_dict
from .manager.data_manager import data_manager, tl
from .utils import logging


def init():
    tl.start()


def get_app_status(hub_uuid: str, app_id: list) -> dict or None:
    if hub_uuid not in hub_dict:
        logging.warning(f"NO HUB: {hub_uuid}")
        return None
    app_status = data_manager.get_app_status(hub_uuid, app_id)
    log_str = ""
    if not app_status['release_info']:
        log_str += "(empty)"
    logging.info(f"已完成单个请求 app_id: {app_id}{log_str} hub_uuid: {hub_uuid}")
    return app_status


def get_app_status_list(hub_uuid: str, app_id_list: list) -> dict or None:
    if hub_uuid not in hub_dict:
        logging.warning(f"NO HUB: {hub_uuid}")
        return None
    app_status_list = {"response": data_manager.get_response_list(hub_uuid, app_id_list)}
    logging.info(f"已完成批量请求 hub_uuid: {hub_uuid}（{len(app_id_list)}）")
    return app_status_list


def get_download_info(hub_uuid: str, app_id: list, asset_index: list) -> dict or None:
    logging.info(f"请求下载资源 app_id: {app_id} hub_uuid: {hub_uuid}")
    download_info = data_manager.get_download_info(hub_uuid, app_id, asset_index)
    logging.info(f"回应下载资源: download_info: {download_info}")
    return download_info
