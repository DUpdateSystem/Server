import json

from app.config import server_config
from .server.api import get_release_list, get_download_info
from .server.utils import logging
from .server.hubs.hub_script_utils import get_session


def _debug(hub_uuid: str, app_id_option):
    server_config.debug_mode = True
    app_id = []
    for i in range(0, len(app_id_option), 2):
        app_id.append({
            "key": app_id_option[i],
            "value": app_id_option[i + 1]
        })
    logging.info(f"开始测试：hub_uuid:{hub_uuid}, app_id:{app_id}")
    logging.info("测试 get_app_status 函数")
    app_status = __get_app_status(hub_uuid, app_id)
    js = json.dumps(app_status, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)
    logging.info("测试 get_download_info 函数")
    row_download_info = get_download_info(hub_uuid, app_id, [0, 0])
    js = json.dumps(row_download_info, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)


def __get_app_status(hub_uuid: str, app_id: list) -> dict:
    app_status = None
    fun_id = 0
    http_response = None
    while not app_status:
        row_app_status = get_release_list(hub_uuid, app_id,
                                          fun_id=fun_id, http_response=http_response,
                                          use_cache=False, cache_data=False)
        if 'http_proxy' in row_app_status:
            http_proxy = row_app_status['http_proxy']
            fun_id = http_proxy['next_fun_id']
            http_proxy_request = http_proxy['http_proxy_request']
            method = http_proxy_request['method']
            url = http_proxy_request['url']
            headers_list = []
            if 'headers' in http_proxy_request:
                headers_list = http_proxy_request['headers']
            body_type = None
            body_text = None
            if 'body' in http_proxy_request:
                body = http_proxy_request['body']
                body_type = body['type']
                body_text = body['text']
            status_code, text = __process_proxy_request(method, url, headers_list, body_type, body_text)
            http_response = {
                'status_code': status_code,
                'text': text
            }
        else:
            app_status = row_app_status['app_status']
    return app_status


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


def debug(hub_uuid: str, app_id_option):
    try:
        _debug(hub_uuid, app_id_option)
    except KeyboardInterrupt:
        logging.info("手动停止 DEBUG")
