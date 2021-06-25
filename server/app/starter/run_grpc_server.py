import asyncio
from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor

from google.protobuf.json_format import ParseDict, MessageToDict
from grpc import RpcContext, aio

from app.grpc_template import route_pb2_grpc
from app.grpc_template.route_pb2 import *
from app.server.api import *
# 初始化配置
from app.server.config import server_config
from app.server.manager.data.constant import logging
from app.server.utils import get_response, grcp_dict_list_to_dict, set_new_asyncio_loop, call_def_in_loop_return_result


class Greeter(route_pb2_grpc.UpdateServerRouteServicer):

    def GetCloudConfig(self, request, context) -> Str:
        rule_hub_url = None
        # noinspection PyBroadException
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            if request["s"] == "dev":
                rule_hub_url = "https://raw.githubusercontent.com/DUpdateSystem/UpgradeAll-rules/" \
                               "dev/rules/rules.json"
                logging.info("使用 Dev 分支的云端配置仓库")
        except Exception:
            pass
        if rule_hub_url is None:
            rule_hub_url = server_config.cloud_rule_hub_url
        response = get_response(rule_hub_url)
        if response:
            logging.info("已完成获取云端配置仓库数据请求")
            return Str(s=response.text)

    def GetAppStatus(self, request, context) -> Response:
        # noinspection PyBroadException
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            hub_uuid: str = request['hub_uuid']
            if 'app_id' in request:
                app_id: list = request['app_id']
            else:
                app_id = []
            app_id_dict = {}
            app_id_row = []
            for i in app_id:
                app_id_dict[i["key"]] = i["value"]
                app_id_row.append({'k': i["key"], 'v': i["value"]})
            new_d = MessageToDict(next(self.__get_app_release(hub_uuid, None, [app_id_dict])),
                                  preserving_proto_field_name=True)
            release = new_d["release"]
            app_id_l = release["app_id"]
            if app_id_row != app_id_l:
                logging.exception(f'gRPC: GetAppStatus: app_id 校验失败'
                                  f'app_id: {app_id_row}, app_id_l: {app_id_l}')
            valid_hub = new_d["valid_hub"]
            release_list = None
            if valid_hub:
                valid_data = "valid_data" in release and release["valid_data"]
                valid_app = valid_data and "release_list" in release and len(release["release_list"]) != 0
                if valid_app:
                    release_list = release["release_list"]
                app_status = {
                    "valid_hub_uuid": valid_hub,
                    "valid_app": valid_app,
                    "valid_data": valid_data,
                    "release_info": release_list
                }
            else:
                app_status = {
                    "valid_hub_uuid": valid_hub,
                }
            return ParseDict({"app_status": app_status}, Response())
        except Exception:
            logging.exception('gRPC: GetAppStatus')
            return None

    def GetDownloadInfo(self, request, context) -> DownloadInfo:
        # noinspection PyBroadException
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            app_id_info = request["app_id_info"]
            hub_uuid = app_id_info["hub_uuid"]
            app_id = app_id_info["app_id"]
            app_id_dict = {}
            for i in app_id:
                app_id_dict[i["key"]] = i["value"]
            asset_index = request["asset_index"]
            new_d = MessageToDict(self.__get_download_info(hub_uuid, None, app_id_dict, asset_index),
                                  preserving_proto_field_name=True)
            if "list" in new_d:
                return ParseDict(new_d["list"][0], DownloadInfo())
        except Exception:
            logging.exception('gRPC: GetDownloadInfo')
            return None

    def InitHubAccount(self, request: AccountRequest, context) -> AccountResponse:
        hub_uuid: str = request.hub_uuid
        account: dict = grcp_dict_list_to_dict(request.account)
        # noinspection PyBroadException
        try:
            return self.__init_account(hub_uuid, account)
        except Exception:
            logging.exception(f'gRPC: InitHubAccount, hub_uuid: {hub_uuid}')
            return None

    def GetAppRelease(self, request: ReleaseRequest, context) -> ReleaseResponse:
        hub_uuid: str = request.hub_uuid
        auth: dict = grcp_dict_list_to_dict(request.auth)
        app_id_list: list = [grcp_dict_list_to_dict(item.app_id) for item in request.app_id_list]
        logging.warning(f"{hub_uuid}, num: {len(app_id_list)}, auth: {auth}")
        # noinspection PyBroadException
        try:
            for item in self.__get_app_release(hub_uuid, auth, app_id_list):
                yield item
        except Exception:
            logging.exception(f'gRPC: GetAppStatus, hub_uuid: {hub_uuid}')
            return None

    def DevGetDownloadInfo(self, request: GetDownloadRequest, context: RpcContext) -> GetDownloadResponse:
        hub_uuid: str = request.hub_uuid
        auth: dict = grcp_dict_list_to_dict(request.auth)
        app_id: dict = grcp_dict_list_to_dict(request.app_id)
        asset_index: list = request.asset_index
        # noinspection PyBroadException
        try:
            return self.__get_download_info_list(hub_uuid, auth, app_id, asset_index)
        except Exception:
            logging.exception(f'gRPC: GetDownloadInfo, hub_uuid: {hub_uuid}')
            return None

    @staticmethod
    def __init_account(hub_uuid: str, account: dict) -> AccountResponse:
        auth_data = init_account(hub_uuid, account)
        return ParseDict(auth_data, AccountResponse())

    @staticmethod
    def __get_app_release(hub_uuid: str, auth: dict or None, app_id_list: list) -> ReleaseResponse:
        for item in get_release_dict(hub_uuid, auth, app_id_list):
            yield ParseDict(item, ReleaseResponse())

    @staticmethod
    def __get_download_info(hub_uuid: str, auth: dict or None, app_id: dict, asset_index: list) -> DownloadInfo:
        download_info = get_download_info(hub_uuid, auth, app_id, asset_index)
        return ParseDict(download_info, DownloadInfo)

    @staticmethod
    def __get_download_info_list(hub_uuid: str, auth: dict or None, app_id: dict,
                                 asset_index: list) -> GetDownloadResponse:
        download_info = get_download_info_list(hub_uuid, auth, app_id, asset_index)
        return ParseDict(download_info, GetDownloadResponse())


__loop = set_new_asyncio_loop()
__server: aio.server
__lock = asyncio.Lock(loop=__loop)


async def __run():
    global __server
    await __lock.acquire()
    __server = aio.server(ThreadPoolExecutor(max_workers=server_config.max_workers))
    route_pb2_grpc.add_UpdateServerRouteServicer_to_server(Greeter(), __server)
    __server.add_insecure_port(f'{server_config.host}:{server_config.port}')
    logging.info("gRPC 启动中")
    await __server.start()
    logging.info("gRPC 已启动")

    # 等待停止信号
    logging.info("启动 gRPC 进程运行阻塞锁（额外）")
    await __lock.acquire()
    logging.info("脱离 gRPC 进程运行阻塞锁（额外）")
    await __server.wait_for_termination()
    logging.info("脱离 gRPC 运行阻塞")


def _run():
    try:
        call_def_in_loop_return_result(__run(), __loop)
        logging.info("gRPC 已脱离阻塞")
    except KeyboardInterrupt:
        logging.info("停止 gRPC")
        stop()


def serve() -> [Process]:
    t = Process(target=_run)
    t.start()
    return t


async def __stop():
    logging.info("gRPC 停止中")
    await __server.stop(5)
    logging.info("gRPC 已停止")
    __lock.release()
    logging.info("已取消 gRPC 进程运行阻塞锁（额外）")


def stop():
    call_def_in_loop_return_result(__stop(), __loop)
