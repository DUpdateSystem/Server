import argparse
import os
import sys
from threading import Thread

from app.server.config import server_config
from app.server.manager.data.constant import logging, time_loop
from app.starter.run_debugger import debug
from app.starter.run_grpc_server import serve, stop
from app.status_checker.http_api import checker_thread


def __run() -> [Thread, Thread or None]:
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

    env_dist = os.environ
    proxy = None
    if 'all_proxy' in env_dist:
        proxy = env_dist['all_proxy']
    elif 'http_proxy' in env_dist:
        proxy = env_dist['http_proxy']
    elif 'https_proxy' in env_dist:
        proxy = env_dist['https_proxy']
    server_config.network_proxy = proxy
    run_args = parser.parse_args()
    server_thread = debug_thread = None

    if run_args.debug:
        # 运行 debug 程序
        debug_thread = Thread(target=debug, args=(run_args.hub_uuid, run_args.test_options, run_args.init_account))
        debug_thread.start()
    else:
        # 运行服务程序
        server_thread = serve()
    return server_thread, debug_thread


def run():
    server_thread = None
    try:
        checker_thread.start()
        server_thread, debug_thread = __run()
        if debug_thread:
            debug_thread.join()
        if server_thread:
            time_loop.start()
            server_thread.join()
    except KeyboardInterrupt:
        logging.info("正在停止")
    finally:
        checker_thread.shutdown()
        if server_thread:
            stop()
            logging.info("已停止")
        sys.exit(0)
