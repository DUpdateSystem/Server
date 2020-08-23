import json

from app.config import server_config
from .server.api import *
from .server.hubs.hub_script_utils import get_session
from .server.utils import logging


def _debug(hub_uuid: str, test_options: dict, run_init_account: bool = False):
    server_config.debug_mode = True
    if run_init_account:
        _init_account_debug(hub_uuid, test_options['account'])
    else:
        _standard_debug(hub_uuid, test_options['auth'], test_options['app_id'])


def _init_account_debug(hub_uuid: str, account: dict):
    logging.info(f"开始测试：hub_uuid: {hub_uuid}, account: {account}")
    logging.info("测试  init_account函数")
    row_download_info = init_account(hub_uuid, account)
    js = json.dumps(row_download_info, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)


def _standard_debug(hub_uuid: str, auth: dict, app_id: dict):
    logging.info(f"开始测试：hub_uuid: {hub_uuid}, app_id: {app_id}, auth: {dict}")
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


auth_key = '_auth'


def debug(hub_uuid: str, test_options: list, run_init_account: bool = False):
    try:
        app_id = {}
        auth = {}
        account = {}
        l_size = len(test_options)
        auth_index = 0
        if run_init_account:
            for i in range(0, l_size, 2):
                account[test_options[i]] = test_options[i + 1]
        else:
            if auth_key in test_options:
                l_size = auth_index = test_options.index(auth_key)
            for i in range(0, l_size, 2):
                app_id[test_options[i]] = test_options[i + 1]
            if auth_index:
                for i in range(auth_index + 1, len(test_options), 2):
                    auth[test_options[i]] = test_options[i + 1]
        test_options = {
            'auth': auth,
            'app_id': app_id,
            'account': account
        }
        _debug(hub_uuid, test_options, run_init_account)
    except KeyboardInterrupt:
        logging.exception("手动停止 DEBUG")
    except TypeError:
        logging.exception("DEBUG 参数不完整")
