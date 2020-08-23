import threading
from concurrent import futures
from threading import Thread

import grpc
from google.protobuf.json_format import ParseDict
from grpc import Server

# 初始化配置
from app.config import server_config
from app.grpc_template import route_pb2_grpc
from app.grpc_template.route_pb2 import *
from app.server.api import *
from app.server.manager.data_manager import tl
from app.server.utils import logging, get_response, grcp_dict_list_to_dict


class Greeter(route_pb2_grpc.UpdateServerRouteServicer):

    def GetCloudConfig(self, request, context) -> Str:
        response = get_response(server_config.cloud_rule_hub_url)
        if response:
            logging.info("已完成获取云端配置仓库数据请求")
            return Str(s=response.text)

    def GetAppStatus(self, request: ReleaseRequest, context) -> ReleaseResponse:
        hub_uuid: str = request.hub_uuid
        auth: dict = grcp_dict_list_to_dict(request.auth)
        app_id_list: list = [grcp_dict_list_to_dict(item) for item in request.app_id_list]
        # noinspection PyBroadException
        try:
            return self.__get_app_status(hub_uuid, auth, app_id_list)
        except Exception:
            logging.exception('gRPC: GetAppStatus')
            return None

    def GetDownloadInfo(self, request, context: grpc.RpcContext) -> DownloadInfo:
        if context.cancel():
            return
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
    def __get_app_status(hub_uuid: str, auth: dict, app_id_list: list) -> ReleaseResponse:
        release_list = get_release_dict(hub_uuid, auth, app_id_list)
        return ParseDict(release_list, ReleaseResponse())

    @staticmethod
    def __get_download_info(hub_uuid: str, auth: dict, app_id: dict, asset_index: list) -> DownloadInfo:
        download_info = get_download_info(hub_uuid, auth, app_id, asset_index)
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
