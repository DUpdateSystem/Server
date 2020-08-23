import json

from app.config import server_config
from .server.api import get_release_dict, get_download_info
from .server.hubs.hub_script_utils import get_session
from .server.utils import logging


def _debug(hub_uuid: str, auth: dict, app_id: dict):
    server_config.debug_mode = True
    logging.info(f"开始测试：hub_uuid:{hub_uuid}, app_id:{app_id}")
    logging.info("测试 get_app_status 函数")
    release_dict = get_release_dict(hub_uuid, auth, [app_id], use_cache=False, cache_data=False)
    js = json.dumps(release_dict, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)
    logging.info("测试 get_download_info 函数")
    row_download_info = get_download_info(hub_uuid, auth, app_id, [0, 0])
    js = json.dumps(row_download_info, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)


def __process_proxy_request(method: str, url: str, headers_list: list, body_type: str, body_text: str) -> [int, str]:
    headers = {}
    for header in headers_list:
        headers[header['key']] = header['value']
    if body_type:
        headers['Content-Type'] = body_type
    if method == "get":
        r = get_session().get(url, headers=headers, data=body_text)
    elif method == 'post':
        r = get_session().post(url, headers=headers, data=body_text)
    else:
        return
    status_code = r.status_code
    text = r.text
    return status_code, text


def debug(hub_uuid: str, app_id_option: list):
    try:
        app_id = {}
        auth = {}
        for i in range(0, len(app_id_option), 2):
            app_id[app_id_option[i]] = app_id_option[i + 1]
        auth_key = '_auth'
        if auth_key in app_id_option:
            auth_index = app_id_option.index(auth_key)
            for i in range(auth_index + 1, len(app_id_option), 2):
                auth[app_id_option[i]] = app_id_option[i + 1]
        _debug(hub_uuid, auth, app_id)
    except KeyboardInterrupt:
        logging.info("手动停止 DEBUG")
