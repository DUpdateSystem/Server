import asyncio
import time

import grpc

from app.grpc_template import route_pb2_grpc, route_pb2
from app.server.config import server_config
from app.server.utils import call_def_in_loop_return_result

__redis_availability_setting_time = time.time()
__redis_availability = True
__timeout = 30

__self_channel = grpc.insecure_channel(f'localhost:{server_config.port}')
__self_stub = route_pb2_grpc.UpdateServerRouteStub(__self_channel)


def get_grpc_available():
    response = call_def_in_loop_return_result(_get_grpc_available())
    return response


async def _get_grpc_available():
    try:
        return await asyncio.wait_for(__get_grpc_available(), timeout=15)
    except asyncio.TimeoutError as e:
        return e


async def __get_grpc_available():
    return __self_stub.GetServerStatus(route_pb2.Empty())


def get_redis_availability() -> bool:
    if not __redis_availability and time.time() - __redis_availability_setting_time < __timeout:
        return False
    else:
        return True


def set_redis_availability(value: bool):
    global __redis_availability
    __redis_availability = value


__hub_available_setting_time_dict = {}

__hub_available_key_list = []


def get_hub_available(hub_uuid: str) -> bool:
    if hub_uuid not in __hub_available_key_list \
            and time.time() - __hub_available_setting_time_dict[hub_uuid] < __timeout:
        return True
    else:
        return True


def set_hub_available(hub_uuid: str, available: bool):
    if available and hub_uuid in __hub_available_setting_time_dict:
        del __hub_available_setting_time_dict[hub_uuid]
        __hub_available_key_list.append(hub_uuid)
    elif not available and hub_uuid in __hub_available_key_list:
        __hub_available_key_list.remove(hub_uuid)
        __hub_available_setting_time_dict[hub_uuid] = time.time()
