import argparse
import os

from app.boot.run_cluster_api import run_cluster_api
from app.boot.run_debugger import debug
from app.boot.run_web_app import run_api, app
from app.database.init import init_database
from app.server.config import server_config
from app.server.manager.data.constant import logging
from app.server.manager.webgetter.getter import web_getter_manager


def __init_env():
    env_dist = os.environ
    proxy = None
    if 'all_proxy' in env_dist:
        proxy = env_dist['all_proxy']
    elif 'http_proxy' in env_dist:
        proxy = env_dist['http_proxy']
    elif 'https_proxy' in env_dist:
        proxy = env_dist['https_proxy']
    server_config.network_proxy = proxy


def init():
    # 避免 flask debug 模式代码重加载导致初始化两次
    if server_config.debug_mode and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return
    __init_env()
    init_database()
    run_cluster_api()


init()


def __run():
    parser = argparse.ArgumentParser(
        prog="DUpdateSystem Server",
        description='DUpdateSystem 服务端'
    )
    parser.add_argument('--normal', action='store_true', default=True,
                        help='以 config.ini 配置正常运行服务端')
    parser.add_argument('--debug', action='store_true', default=False, help='运行软件源脚本测试')
    parser.add_argument('hub_uuid', type=str, nargs='?', help='测试的软件源脚本的 UUID')
    parser.add_argument('--init_account', action='store_true', default=False, help='测试的软件源脚本的帐号初始化函数')
    parser.add_argument('--test_options', type=str, nargs='*', default=None,
                        help='测试软件源脚本的运行选项，以 key value 为组，例如：android_app_package net.xzos.upgradeall')

    run_args = parser.parse_args()

    if run_args.debug:
        # 运行 debug 程序
        debug(run_args.hub_uuid, run_args.test_options, run_args.init_account)
    else:
        # 运行服务程序
        run_api()


def __stop():
    web_getter_manager.stop()


def run():
    try:
        __run()
    except KeyboardInterrupt:
        logging.info("正在停止")
        __stop()
    except Exception as e:
        logging.exception(e)
    finally:
        logging.info("已停止")


# 只是个占位符
app = app