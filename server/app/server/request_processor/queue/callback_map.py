import threading
import time
from multiprocessing import JoinableQueue
from queue import Empty

from app.server.config import server_config
from app.server.manager.data.constant import logging
from app.server.utils.var_barrier import VarBarrier

args_map_key_proxy = JoinableQueue()

callback_map_lock = threading.Lock()
callback_map = {}

# 启动清理事件
clean_wait_barrier = VarBarrier()

timeout = server_config.network_timeout


def call_callback(key, *args):
    args_map_key_proxy.put((key, args))


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
        clean_wait_barrier.register()
        __check_callback_polling()
        clean_wait_barrier.unregister()


def __check_callback_polling():
    while callback_map:
        try:
            key, args = args_map_key_proxy.get(timeout / 3)
            args_map_key_proxy.task_done()
            clean_wait_barrier.wait()
            __call_callback(key, args)
        except Empty:
            pass
        except KeyError:
            pass
        check_callback_timeout()


def __call_callback(key, args):
    with callback_map_lock:
        for callback, timestamp in callback_map.pop(key):
            if check_timeout(timestamp):
                try:
                    callback(*args)
                except Exception as e:
                    logging.exception(e)


def check_callback_timeout():
    with callback_map_lock:
        for key, callback_list in list(callback_map.items()):
            for callback_item in callback_list:
                callback, timestamp = callback_item
                if not check_timeout(timestamp):
                    callback_list.remove(callback_item)
            if not callback_list:
                del callback_map[key]


def check_timeout(timestamp) -> bool:
    return time.time() - timestamp <= server_config.network_timeout
