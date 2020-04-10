import logging
import os
import sys
from concurrent import futures

import grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.grpc_server import route_pb2_grpc
from app.grpc_server.route_pb2 import AppStatus, ResponsePackage, ResponseList

# 初始化配置
from app.config import server_config
from app.server.manager.data_manager import data_manager
from app.server.hubs.library.hub_list import hub_dict


class Greeter(route_pb2_grpc.UpdateServerRouteServicer):

    def GetAppStatus(self, request, context) -> AppStatus:
        hub_uuid = request.hub_uuid
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return AppStatus(valid_hub_uuid=False)
        app_id: list = request.app_id
        logging.info(f"已完成单个请求: {app_id}")
        return data_manager.get_app_status(hub_uuid, app_id)

    def GetAppStatusList(self, request, context) -> ResponseList:
        hub_uuid = request.hub_uuid
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return ResponseList(
                response=[ResponsePackage(app_status=AppStatus(valid_hub_uuid=False))]
            )
        app_id_list = []
        for app_id in request.app_id_list:
            app_id_list.append(app_id.app_id)
        logging.info(f"已完成批量请求（{len(app_id_list)}）")
        return ResponseList(
            response=data_manager.get_response_list(hub_uuid, app_id_list)
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=server_config.max_workers))
    route_pb2_grpc.add_UpdateServerRouteServicer_to_server(Greeter(), server)
    server.add_insecure_port(f'{server_config.host}:{server_config.port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
