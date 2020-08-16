import threading
from concurrent import futures
from threading import Thread

import grpc
from google.protobuf.json_format import MessageToDict, ParseDict
from grpc import Server

# 初始化配置
from app.config import server_config
from app.grpc_template import route_pb2_grpc
from app.grpc_template.route_pb2 import *
from app.server.api import *
from app.server.manager.data_manager import tl
from app.server.utils import logging, get_response


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
            fun_id: int = 0
            http_response = None
            if 'http_proxy' in request:
                fun_id = request['http_proxy']['fun_id']
                http_response = request['http_proxy']['http_response']
            return self.__get_app_status(hub_uuid, app_id, fun_id, http_response)
        except Exception:
            logging.exception('gRPC: GetAppStatus')
            return None

    def GetAppStatusList(self, request, context) -> ResponseList:
        # noinspection PyBroadException
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            hub_uuid: str = request['hub_uuid']
            app_id_list: list = request['app_id_list']
            return self.__get_app_l
                ist_status(hub_uuid, app_id_list)
        except Exception:
            logging.exception('gRPC: GetAppStatusList')
            return None

    def GetDownloadInfo(self, request, context: grpc.RpcContext) -> DownloadInfo:
        if context.cancel():
            return
        # noinspection PyBroadException
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            app_id_info = request["app_id_info"]
            hub_uuid = app_id_info["hub_uuid"]
            app_id = app_id_info["app_id"]
            asset_index = request["asset_index"]
            return self.__get_download_info(hub_uuid, app_id, asset_index)
        except Exception:
            logging.exception('gRPC: GetDownloadInfo')
            return None

    @staticmethod
    def __get_app_status(hub_uuid: str, app_id: list,
                         fun_id: int = 0, http_response: dict = None) -> Response:
        app_status = get_app_status(hub_uuid, app_id, fun_id, http_response)
        if app_status is None:
            return Response(app_status=AppStatus(valid_hub_uuid=False))
        return ParseDict(app_status, Response())

    @staticmethod
    def __get_app_list_status(hub_uuid: str, app_id_list: list) -> ResponseList:
        app_status_list = get_app_list_status(hub_uuid, app_id_list)
        return ParseDict({"response": app_status_list}, ResponseList())

    @staticmethod
    def __get_download_info(hub_uuid: str, app_id: list, asset_index: list) -> DownloadInfo:
        download_info = get_download_info(hub_uuid, app_id, asset_index)
        if not download_info:
            download_info = {}
        return ParseDict(download_info, DownloadInfo())


def init():
    if not server_config.debug_mode:
        tl.start()


def serve() -> [Server, Thread]:
    init()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=server_config.max_workers))
    route_pb2_grpc.add_UpdateServerRouteServicer_to_server(Greeter(), server)
    server.add_insecure_port(f'{server_config.host}:{server_config.port}')
    server.start()
    t = threading.Thread(target=server.wait_for_termination)
    t.start()
    return server, t
