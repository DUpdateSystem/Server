import asyncio

from app.server.utils import (logging, set_new_asyncio_loop, call_def_in_loop, call_def_in_loop_return_result,
                              get_manager_value, get_manager_list, get_manager_dict)
from .utils import get_key, ProxyKilledError


class ClientProxy:
    # 获取 http 请求主协程
    __loop = set_new_asyncio_loop()
    # 发送下一个请求协程
    __wait_cond = asyncio.Condition()
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
        request = call_def_in_loop_return_result(
            self.__get_request(), self.__loop
        )
        logging.info(f'c{self.index}：发送代理请求')
        return request

    def stop(self):
        self.__running.set(False)
        for key in self.__lock_dict.keys():
            call_def_in_loop(
                self.__unlock_request_wait(key),
                self.__loop
            )
        self.__wait_cond.notify()
        self.__loop.stop()

    @property
    def index(self):
        return self.__index

    def http_request(self, method: str, url: str, headers: dict or None,
                     body_type: str or None, body_text: str or None) -> dict:
        if headers is None:
            headers = {}
        return call_def_in_loop_return_result(
            self.__http_request(method, url, headers, body_type, body_text),
            self.__loop
        )

    def check_proxy_status(self, key: str) -> bool:
        return key in self.__lock_dict and self.__running.value

    async def __http_request(self, method: str, url: str, headers: dict,
                             body_type: str or None, body_text: str or None) -> dict:
        logging.info("input")
        key = get_key(method, url, headers, body_type, body_text)
        # 输入队列
        self.__add_request_queue(key, method, url, headers, body_type, body_text)
        # 等待返回
        await self.__set_request_lock(key)
        # 检查运行状态
        if not self.__running.value:
            raise ProxyKilledError(self.index)
        # 获取返回数据
        return await self.__get_response(key)

    def push_response(self, key: str, status_code: int, response: str):
        logging.info(f'c{self.index}：接收代理返回')
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
            cond = d["cond"]
            cond.notify_all()  # 解锁

    async def __set_request_lock(self, key: str):
        cond = call_def_in_loop_return_result(
            self.__get_request_lock(key),
            self.__loop
        )
        async with cond:
            await cond.wait()

    async def __get_request_lock(self, key: str):
        with await self.__lock_dict_lock:
            lock_dict = self.__lock_dict
            if key in lock_dict:
                d = lock_dict[key]
                d["used"] += 1
                cond = d["cond"]
            else:
                cond = asyncio.Condition()
                lock_dict[key] = {
                    "used": 1,
                    "cond": cond
                }
        return cond

    async def __get_response(self, key: str) -> dict:
        with await self.__lock_dict_lock:
            lock_dict = self.__lock_dict
            if key in lock_dict:
                d = lock_dict[key]
                d["used"] -= 1
                if d["used"] > 0:
                    return self.__response_dict[key]
                else:
                    del lock_dict[key]
                    return self.__response_dict.pop(key)

    async def __get_request(self):
        if not self.__request_queue:
            wait = self.__wait_cond
            async with wait:
                await wait.wait()
        # 检查运行状态
        if not self.__running.value:
            raise ProxyKilledError(self.index)
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
        self.__wait_cond.notify()
