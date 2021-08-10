import argparse
import os
import sys
from multiprocessing import Process
from threading import Thread

from app.server.config import server_config
from app.server.manager.data.constant import logging
from app.server.manager.webgetter.getter import web_getter_manager
from app.starter.run_debugger import debug
from app.starter.run_grpc_server import stop
from app.status_checker.http_api import checker_thread
from app.web_api.app import app


def __run() -> [Process, Thread or None]:
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
    server_process = debug_thread = None
    web_getter_manager.start()

    if run_args.debug:
        # 运行 debug 程序
        debug_thread = Thread(target=debug, args=(run_args.hub_uuid, run_args.test_options, run_args.init_account))
        debug_thread.start()
    else:
        # 运行服务程序
        pass
        # server_process = serve()
    return server_process, debug_thread


def run():
    server_process = None
    try:
        checker_thread.start()
        server_process, debug_thread = __run()
        if debug_thread:
            debug_thread.join()
            web_getter_manager.stop()
        app.run(host='0.0.0.0', port=5255)
        if server_process:
            # start_schedule()
            server_process.join()
        web_getter_manager.join()
    except KeyboardInterrupt:
        logging.info("正在停止")
        web_getter_manager.stop()
        stop()
    except Exception as e:
        logging.exception(e)
    finally:
        checker_thread.shutdown()
        if server_process:
            server_process.kill()
            logging.info("已停止")
        sys.exit(0)
