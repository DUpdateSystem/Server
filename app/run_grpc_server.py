import traceback
from concurrent import futures

import grpc
from google.protobuf.json_format import MessageToDict, ParseDict

# 初始化配置
from app.config import server_config
from app.grpc_template import route_pb2_grpc
from app.grpc_template.route_pb2 import AppStatus, ResponseList, DownloadInfo
from app.server.api import init, get_app_status, get_app_status_list, get_download_info
from app.server.utils import logging


class Greeter(route_pb2_grpc.UpdateServerRouteServicer):

    def GetAppStatus(self, request, context) -> AppStatus:
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            hub_uuid: str = request['hub_uuid']
            app_id: list = request['app_id']
            return self.__get_app_status(hub_uuid, app_id)
        except Exception:
            logging.error(traceback.format_exc())
            return None

    def GetAppStatusList(self, request, context) -> ResponseList:
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            hub_uuid: str = request["hub_uuid"]
            app_id_list: list = [item['app_id'] for item in request["app_id_list"]]
            return self.__get_app_status_list(hub_uuid, app_id_list)
        except Exception:
            logging.error(traceback.format_exc())
            return None

    def GetDownloadInfo(self, request, context) -> DownloadInfo:
        try:
            request = MessageToDict(request, preserving_proto_field_name=True)
            app_id_info = request["app_id_info"]
            hub_uuid = app_id_info["hub_uuid"]
            app_id = app_id_info["app_id"]
            asset_index = request["asset_index"]
            return self.__get_download_info(hub_uuid, app_id, asset_index)
        except Exception:
            logging.error(traceback.format_exc())
            return None

    @staticmethod
    def __get_app_status(hub_uuid: str, app_id: list) -> AppStatus:
        app_status = get_app_status(hub_uuid, app_id)
        if app_status is None:
            return AppStatus(valid_hub_uuid=False)
        return ParseDict(app_status, AppStatus())

    @staticmethod
    def __get_app_status_list(hub_uuid: str, app_id_list: list) -> ResponseList:
        app_status_list = get_app_status_list(hub_uuid, app_id_list)
        if app_status_list is None:
            return ResponseList(app_status=AppStatus(valid_hub_uuid=False))
        return ParseDict(app_status_list, ResponseList())

    @staticmethod
    def __get_download_info(hub_uuid: str, app_id: list, asset_index: list) -> AppStatus:
        return ParseDict(get_download_info(hub_uuid, app_id, asset_index), DownloadInfo())


def serve():
    init()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=server_config.max_workers))
    route_pb2_grpc.add_UpdateServerRouteServicer_to_server(Greeter(), server)
    server.add_insecure_port(f'{server_config.host}:{server_config.port}')
    server.start()
    server.wait_for_termination()
