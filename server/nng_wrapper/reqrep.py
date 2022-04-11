import time

from pynng import Rep0, Socket

from config import timeout_api

time_length = 19
time_temp = "%Y-%m-%d-%H:%M:%S"


def get_localtime_str() -> str:
    return time.strftime(time_temp, time.localtime())


def dump_time_str_to_int(time_str: str) -> float:
    time_i = time.mktime(time.strptime(time_str, time_temp))
    return time_i


def check_time(request: str, timeout: int = timeout_api) -> bool:
    time_str = request[:time_length]
    return dump_time_str_to_int(time_str) - time.time() <= timeout


async def arecv_msg(socket: Socket):
    data = (await socket.arecv_msg()).bytes
    time_str = data[:19].decode()
    if check_time(time_str):
        return data[19:]
    else:
        raise TimeoutError


async def asend(socket: Socket, data: bytes):
    time_bytes = get_localtime_str().encode()
    data = time_bytes + data
    return await socket.asend(data)


async def send_rep_with_id(socket: Rep0, msg_id, rep_msg: bytes) -> str:
    await socket.asend(msg_id + rep_msg)
    return msg_id
