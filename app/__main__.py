import argparse

from app.run_debugger import debug
from app.run_grpc_server import serve


def make_action():
    class RunServerAction(argparse.Action):
        def __call__(self, *args, **kwargs):
            serve()

    return RunServerAction


def main():
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
    if run_args.debug:
        debug(run_args.hub_uuid, run_args.hub_options)
    elif run_args.normal:
        serve()


if __name__ == '__main__':
    main()
