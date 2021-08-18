import json

from app.server.api import *
from app.server.config import server_config
from app.server.manager.data.constant import logging


def _debug(hub_uuid: str, test_options: dict, run_init_account: bool = False):
    server_config.debug_mode = True
    if run_init_account:
        _init_account_debug(hub_uuid, test_options['account'])
    else:
        _standard_debug(hub_uuid, test_options['auth'], test_options['app_id'])


def _init_account_debug(hub_uuid: str, account: dict):
    logging.info(f"开始测试：hub_uuid: {hub_uuid}, account: {json.dumps(account)}")
    logging.info("测试 init_account 函数")
    row_download_info = init_account(hub_uuid, account)
    js = json.dumps(row_download_info, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)


def _standard_debug(hub_uuid: str, auth: dict, app_id: dict):
    logging.info(f"开始测试：hub_uuid: {hub_uuid}, app_id: {json.dumps(app_id)}, auth: {json.dumps(auth)}")
    logging.info("测试 get_app_status 函数")
    for release_dict in get_release_dict(hub_uuid, auth, app_id, use_cache=False, cache_data=False):
        js = json.dumps(release_dict, sort_keys=True, indent=4, ensure_ascii=False)
        logging.debug(js)
    logging.info("测试 get_download_info 函数")
    row_download_info = get_download_info_list(hub_uuid, auth, app_id, [0, 0])
    js = json.dumps(row_download_info, sort_keys=True, indent=4, ensure_ascii=False)
    logging.debug(js)


auth_key = '_auth'


def debug(hub_uuid: str, test_options: list, run_init_account: bool = False):
    app_id = {}
    auth = {}
    account = {}
    if test_options:
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
