import threading
from concurrent import futures
from threading import Thread

import grpc
from google.protobuf.json_format import ParseDict, MessageToDict
from grpc import Server

from app.grpc_template import route_pb2_grpc
from app.grpc_template.route_pb2 import *
from app.server.api import *
# 初始化配置
from app.server.config import server_config
from app.server.manager.data.constant import logging, time_loop
from app.server.utils import get_response, grcp_dict_list_to_dict


class Greeter(route_pb2_grpc.UpdateServerRouteServicer):

    def GetCloudConfig(self, request, context) -> Str:
        response = get_response(server_config.cloud_rule_hub_url)
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
            valid_app = not (release["valid_data"] and "release_list" in release and not release["release_list"])
            release_list = None
            if valid_app:
                release_list = release["release_list"]
            if valid_hub:
                app_status = {
                    "valid_hub_uuid": valid_hub,
                    "valid_app": valid_app,
                    "valid_data": release["valid_data"],
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
            logging.exception('gRPC: InitHubAccount')
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
            logging.exception('gRPC: GetAppStatus')
            return None

    def DevGetDownloadInfo(self, request: GetDownloadRequest, context: grpc.RpcContext) -> GetDownloadResponse:
        hub_uuid: str = request.hub_uuid
        auth: dict = grcp_dict_list_to_dict(request.auth)
        app_id: dict = grcp_dict_list_to_dict(request.app_id)
        asset_index: list = request.asset_index
        # noinspection PyBroadException
        try:
            return self.__get_download_info(hub_uuid, auth, app_id, asset_index)
        except Exception:
            logging.exception('gRPC: GetDownloadInfo')
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
    def __get_download_info(hub_uuid: str, auth: dict or None, app_id: dict, asset_index: list) -> GetDownloadResponse:
        download_info = get_download_info(hub_uuid, auth, app_id, asset_index)
        return ParseDict(download_info, GetDownloadResponse())


def init():
    if not server_config.debug_mode:
        time_loop.start()


def serve() -> [Server, Thread]:
    init()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=server_config.max_workers))
    route_pb2_grpc.add_UpdateServerRouteServicer_to_server(Greeter(), server)
    server.add_insecure_port(f'{server_config.host}:{server_config.port}')
    server.start()
    t = threading.Thread(target=server.wait_for_termination)
    t.start()
    return server, t
