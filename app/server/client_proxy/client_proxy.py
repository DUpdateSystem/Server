import asyncio

from app.server.utils import set_new_asyncio_loop, call_def_in_loop, call_def_in_loop_return_result
from .data import get_manager_value, get_manager_list, get_manager_dict


class ClientProxy:
    # 获取 http 请求主协程
    __loop = set_new_asyncio_loop()
    # 发送下一个请求协程
    __wait_next_task = asyncio.Event()
    # 等待客户端回应协程存储字典
    __lock_dict = {}  # 请求数据字典
    __lock_dict_lock = asyncio.Lock()

    # 请求队别
    __request_queue = get_manager_list()
    # 客户端回应数据存储
    __response_dict = get_manager_dict()  # 接受数据字典，key: Lock, value: response json

    def __init__(self, index: int):
        self.__index = index
        # 停止控制
        self.__running = get_manager_value(f"c{index}-run", True)

    def __iter__(self):
        return self

    def __next__(self):
        return self.__get_request()

    def stop(self):
        self.__running.set(False)
        for key in self.__lock_dict.keys():
            call_def_in_loop(
                self.__unlock_request_wait(key),
                self.__loop
            )

    @property
    def index(self):
        return self.__index

    def http_request(self, method: str, url: str, headers: dict or None,
                     body_type: str or None, body_text: str or None) -> dict:
        if headers is None:
            headers = {}
        response = self.__http_request_async(method, url, headers, body_type, body_text)
        return response

    def __http_request_async(self, method: str, url: str, headers: dict,
                             body_type: str or None, body_text: str or None) -> dict:
        key = self.__get_key(method, url, headers, body_type, body_text)
        # 输入队列
        self.__add_request_queue(key, method, url, headers, body_type, body_text)
        # 等待返回
        self.__set_request_lock(key)
        # 检查运行状态
        if not self.__running.value:
            raise KeyboardInterrupt
        # 获取返回数据
        return call_def_in_loop_return_result(
            self.__get_response(key),
            self.__loop
        )

    def push_response(self, key: str, status_code: int, response: str):
        self.__response_dict[key] = {
            "code": status_code,
            "text": response
        }
        call_def_in_loop(
            self.__unlock_request_wait(key),
            self.__loop
        )

    def get_first_request_item(self):
        return {
            "method": "id",
            "key": str(self.index)
        }

    async def __unlock_request_wait(self, key: str):
        async with self.__lock_dict_lock:
            d = self.__lock_dict[key]
            task = d["task"]
            self.__loop.call_soon_threadsafe(task.set)  # 解锁

    def __set_request_lock(self, key: str):
        task = call_def_in_loop_return_result(
            self.__get_request_lock(key),
            self.__loop
        )
        call_def_in_loop(
            task.wait(), self.__loop
        )

    async def __get_request_lock(self, key: str):
        with await self.__lock_dict_lock:
            lock_dict = self.__lock_dict
            if key in lock_dict:
                d = lock_dict[key]
                d["used"] += 1
                task = d["task"]
            else:
                task = asyncio.Event(loop=self.__loop)
                lock_dict[key] = {
                    "task": task,
                    "used": 1
                }
        return task

    async def __get_response(self, key: str) -> dict:
        with await self.__lock_dict_lock:
            lock_dict = self.__lock_dict
            if key in lock_dict:
                d = lock_dict[key]
                if d["used"]:
                    d["used"] -= 1
                    return self.__response_dict[key]
                else:
                    return self.__response_dict.pop(key)

    def __get_request(self):
        request_queue = self.__request_queue
        if not len(request_queue):
            call_def_in_loop(
                self.__wait_next_task.wait(),
                self.__loop
            )
        self.__wait_next_task.clear()
        return self.__request_queue.pop(0)

    def __add_request_queue(self, key: str, method: str, url: str, headers: dict,
                            body_type: str or None, body_text: str or None):
        # 构建请求数据字典
        data_key = key
        # 请求头数据
        headers_list = []
        for key, value in headers.items():
            headers_list.append({
                "key": key,
                "value": value
            })
        # 请求体数据
        if not body_type or not body_text:
            body = None
        else:
            body = {
                "type": body_type,
                "text": body_text
            }
        # 组装数据字典
        request = {
            "key": data_key,
            "method": method,
            "url": url,
            "headers": headers_list,
            "body": body
        }
        self.__request_queue.append(request)
        self.__loop.call_soon_threadsafe(
            self.__wait_next_task.set
        )

    @staticmethod
    def __get_key(method: str, url: str, headers: dict or None,
                  body_type: str or None, body_text: str or None) -> str:
        key = f"{method}-{url}-{headers}"
        if body_type and body_text:
            key += f"-{body_type}-{body_text}"
        return key
