import asyncio

from app.server.utils import set_new_asyncio_loop
from .data import get_manager_list, get_manager_dict


class ClientProxy:
    # 获取 http 请求主协程
    __loop = set_new_asyncio_loop()
    # 发送下一个请求协程
    __wait_next_loop = set_new_asyncio_loop()
    __wait_next_task = asyncio.Event()
    # 等待客户端回应协程存储字典
    __lock_dict = {}  # 请求数据字典
    __lock_dict_lock = asyncio.Lock()

    # 请求队别
    __request_queue = get_manager_list()
    # 客户端回应数据存储
    __response_dict = get_manager_dict()  # 接受数据字典，key: Lock, value: response json

    def __init__(self, index):
        self.__index = index

    def __iter__(self):
        return self

    def __next__(self):
        return self.__get_request()

    def get_index(self):
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
        self.__set_url_lock(key)
        # 获取返回数据
        return self._call_def_in_loop_return_result(
            self.__get_response(key),
            self.__loop
        )

    def push_response(self, key: str, status_code: int, response: str):
        self.__response_dict[key] = {
            "code": status_code,
            "text": response
        }
        self._call_def_in_loop(
            self.__unlock_request_wait(key),
            self.__loop
        )

    def get_first_request_item(self):
        return {
            "method": "id",
            "url": str(self.get_index())
        }

    async def __unlock_request_wait(self, url: str):
        async with self.__lock_dict_lock:
            d = self.__lock_dict[url]
            loop = d["loop"]
            task = d["task"]
            loop.call_soon_threadsafe(task.set())  # 解锁

    def __set_url_lock(self, key: str):
        loop, task = self._call_def_in_loop_return_result(
            self.__get_request_lock_loop(key),
            self.__loop
        )
        self._call_def_in_loop(
            task.wait(), loop
        )

    async def __get_request_lock_loop(self, key: str):
        with await self.__lock_dict_lock:
            lock_dict = self.__lock_dict
            if key in lock_dict:
                d = lock_dict[key]
                d["used"] += 1
                loop = d["loop"]
                task = d["task"]
            else:
                loop = set_new_asyncio_loop()
                task = asyncio.Event(loop=loop)
                lock_dict[key] = {
                    "loop": loop,
                    "task": task,
                    "used": 1
                }
        return loop, task

    async def __get_response(self, key: str) -> dict:
        with await self.__lock_dict_lock:
            lock_dict = self.__lock_dict
            if key in lock_dict:
                d = lock_dict[key]
                if d["used"]:
                    d["used"] -= 1
                    return self.__response_dict[key]
                else:
                    lock_dict.pop(key)["loop"].close()
                    return self.__response_dict.pop(key)

    def __get_request(self):
        request_queue = self.__request_queue
        if not len(request_queue):
            self._call_def_in_loop(
                self.__wait_next_task.wait(),
                self.__wait_next_loop
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
        self.__wait_next_loop.call_soon_threadsafe(
            self.__wait_next_task.set()
        )

    @staticmethod
    def __get_key(method: str, url: str, headers: dict or None,
                  body_type: str or None, body_text: str or None) -> str:
        key = f"{method}-{url}-{headers}"
        if body_type and body_text:
            key += f"-{body_type}-{body_text}"
        return key

    @staticmethod
    def _call_def_in_loop_return_result(core, loop):
        if loop.is_running():
            future = asyncio.run_coroutine_threadsafe(core, loop)
            return future.result()
        else:
            return loop.run_until_complete(core)

    @staticmethod
    def _call_def_in_loop(core, loop):
        if loop.is_running():
            asyncio.run_coroutine_threadsafe(core, loop)
        else:
            loop.run_until_complete(core)
