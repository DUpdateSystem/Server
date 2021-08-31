import threading
import time
from multiprocessing import Event, Lock

from app.server.config import server_config
from app.server.manager.data.constant import logging
from app.server.utils.utils import get_manager_dict
from app.server.utils.var_barrier import VarBarrier

args_map_lock = Lock()
args_map = get_manager_dict()
# 等待写入事件
call_wait_event = Event()

callback_map_lock = threading.Lock()
callback_map = {}

# 启动清理事件
clean_wait_barrier = VarBarrier()

timeout = server_config.network_timeout


def call_callback(key, *args):
    with args_map_lock:
        args_map[key] = args
        call_wait_event.set()

        # 等待清理
        clean_wait_barrier.only_wait()

        call_wait_event.clear()
        del args_map[key]


def add_callback(key, callback):
    with callback_map_lock:
        try:
            callback_list = callback_map[key]
        except KeyError:
            callback_list = []
            callback_map[key] = callback_list
        callback_list.append((callback, time.time()))
    start_check_callback_polling()


checker_lock = threading.Lock()


def start_check_callback_polling():
    threading.Thread(target=check_callback_polling).start()


def check_callback_polling():
    with checker_lock:
        __check_callback_polling()


def __check_callback_polling():
    clean_wait_barrier.register()

    while callback_map:
        if call_wait_event.wait(15 / 3):
            try:
                key, args = next(iter(args_map.items()))
                clean_wait_barrier.wait()
                __call_callback(key, args)
            except KeyError:
                pass
        check_callback_timeout()
    clean_wait_barrier.unregister()


def __call_callback(key, args):
    with callback_map_lock:
        for callback, timestamp in callback_map.pop(key):
            if check_timeout(timestamp):
                try:
                    callback(*args)
                except Exception as e:
                    logging.exception(e)


def check_callback_timeout():
    for key, callback_list in callback_map.items():
        for callback_item in callback_list:
            callback, timestamp = callback_item
            if not check_timeout(timestamp):
                callback_list.remove(callback_item)
        if not callback_list:
            del callback_map[key]


def check_timeout(timestamp) -> bool:
    return time.time() - timestamp <= server_config.network_timeout
