import argparse
import sys
from threading import Thread

from grpc import Server

from app.server.manager.data.constant import logging
from app.starter.run_debugger import debug
from app.starter.run_grpc_server import serve


def __run() -> [Server, Thread, Thread or None]:
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
    server = server_thread = debug_thread = None
    if run_args.debug:
        # 运行 debug 程序
        debug_thread = Thread(target=debug, args=(run_args.hub_uuid, run_args.test_options, run_args.init_account))
        debug_thread.start()
    else:
        # 运行服务程序
        server, server_thread = serve()
    return server, server_thread, debug_thread


def run():
    server = None
    try:
        server, server_thread, debug_thread = __run()
        if debug_thread:
            debug_thread.join()
            server.stop(5).wait()
        if server_thread:
            server_thread.join()
    except KeyboardInterrupt:
        logging.info("正在停止")
    finally:
        if server:
            server.stop(5).wait()
            logging.info("已停止")
        sys.exit(0)
