import os
import sys
from concurrent import futures
import logging

import grpc

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.grpc_server import route_pb2, route_pb2_grpc

# 初始化配置
from app.server.config import server_config
from app.server.manager.data_manager import data_manager
from app.server.hubs.library.hub_list import hub_dict


class Greeter(route_pb2_grpc.UpdateServerRouteServicer):

    def GetReleaseInfo(self, request, context):
        hub_uuid = request.hub_uuid
        if hub_uuid not in hub_dict:
            logging.warning(f"NO HUB: {hub_uuid}")
            return route_pb2.ReturnValue(valid_hub_uuid=False)
        app_info: list = request.app_info
        return_list = data_manager.get_release_info(hub_uuid, app_info)
        valid_app = False
        if return_list:
            valid_app = True
        return route_pb2.ReturnValue(valid_hub_uuid=True, valid_app=valid_app, release_info=return_list)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=server_config.max_workers))
    route_pb2_grpc.add_UpdateServerRouteServicer_to_server(Greeter(), server)
    server.add_insecure_port(f'{server_config.host}:{server_config.port}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
