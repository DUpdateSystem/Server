import argparse
import sys
from threading import Thread

from grpc import Server

from app.run_debugger import debug
from app.run_grpc_server import serve
from app.server.utils import logging


def __run() -> [Server, Thread, Thread or None]:
    parser = argparse.ArgumentParser(
        prog="DUpdateSystem Server",
        description='DUpdateSystem 服务端'
    )
    parser.add_argument('--normal', action='store_true', default=True,
                        help='以 config.ini 配置正常运行服务端')
    parser.add_argument('--debug', action='store_true', default=False, help='运行软件源脚本测试')
    parser.add_argument('hub_uuid', type=str, nargs='?', help='测试的软件源脚本的 UUID')
    parser.add_argument('hub_options', type=str, nargs='*', default=None,
                        help='测试软件源脚本的运行选项，以 key value 为组，例如：android_app_package net.xzos.upgradeall')

    run_args = parser.parse_args()
    # 运行服务程序
    server, server_thread = serve()
    # 运行 debug 程序
    debug_thread = None
    if run_args.debug:
        debug_thread = Thread(target=debug, args=(run_args.hub_uuid, run_args.hub_options))
        debug_thread.start()
    return server, server_thread, debug_thread


def run():
    server = None
    try:
        server, server_thread, debug_thread = __run()
        if debug_thread:
            debug_thread.join()
            server.stop(5).wait()
        server_thread.join()
    except KeyboardInterrupt:
        logging.info("正在停止")
    finally:
        server.stop(5).wait()
        logging.info("已停止")
        sys.exit(0)