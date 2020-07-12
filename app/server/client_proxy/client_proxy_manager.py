import asyncio
import random

from requests import HTTPError

from app.server.utils import (logging, set_new_asyncio_loop, call_def_in_loop_return_result,
                              get_manager_value, get_manager_lock)
from .client_proxy import ClientProxy
from .utils import get_key, ProxyKilledError


class ClientProxyManager:
    __loop = set_new_asyncio_loop()
    __wait_pool_task = asyncio.Event()
    __proxy_pool_lock = get_manager_lock()
    __proxy_pool = []
    __proxy_request_dict_lock = get_manager_lock()
    __proxy_request_dict = {}  # key: 接受处理的客户端代理
    __client_proxy_index = get_manager_value("client_proxy_index", 0)
    __running = get_manager_value("client_proxy_manager_run", True)

    def new_client_proxy(self) -> ClientProxy:
        index = self.__client_proxy_index
        index.value += 1
        client_proxy = ClientProxy(index.value)
        ClientProxyManager.add_proxy(client_proxy)
        return client_proxy

    def proxy_get(self, url: str, headers: dict or None = None):
        return self.__call_proxy("get", url, headers, None, None)

    def proxy_post(self, url: str, headers: dict or None = None,
                   body_type: str or None = None, body_text: str or None = None):
        return self.__call_proxy("post", url, headers, body_type, body_text)

    def __call_proxy(self, method: str, url: str, headers: dict or None,
                     body_type: str or None, body_text: str or None) -> str or None:
        response = self.__run_proxy(method, url, headers, body_type, body_text)
        # 检查 HTTP 数据
        status_code = response["code"]
        if status_code < 200 or status_code >= 400:
            raise HTTPError()
        return response["text"]

    # 向客户端发送代理请求
    def __run_proxy(self, method: str, url: str, headers: dict or None,
                    body_type: str or None, body_text: str or None) -> dict:
        self.__wait_proxy_pool()
        # 检查运行状态
        if not self.__running.value:
            raise KeyboardInterrupt
        client_proxy = self.__get_proxy_client(method, url, headers, body_type, body_text)
        try:
            return client_proxy.http_request(method, url, headers, body_type, body_text)
        except ProxyKilledError:
            self.__run_proxy(method, url, headers, body_type, body_text)

    # 获取代理客户端
    def __get_proxy_client(self, method: str, url: str, headers: dict or None,
                           body_type: str or None, body_text: str or None) -> ClientProxy:
        key = get_key(method, url, headers, body_type, body_text)
        # 检查运行中的代理客户端
        with self.__proxy_request_dict_lock:
            proxy_request_dict = self.__proxy_request_dict
            if key in proxy_request_dict:
                client_proxy = proxy_request_dict[key]
                # 检查代理是否有效
                if client_proxy.check_proxy_status(key):
                    return client_proxy
                else:
                    del proxy_request_dict[key]
            # 随机选取客户端
            with self.__proxy_pool_lock:
                client_proxy: ClientProxy = random.choice(self.__proxy_pool)
            proxy_request_dict[key] = client_proxy
        return client_proxy

    # 等待代理池准备就绪
    def __wait_proxy_pool(self):
        # 检查代理池
        with self.__proxy_pool_lock:
            empty = len(self.__proxy_pool) == 0
        if empty:
            call_def_in_loop_return_result(
                self.__wait_pool_task.wait(),
                self.__loop
            )
        else:
            self.__loop.call_soon_threadsafe(
                self.__wait_pool_task.clear
            )

    def add_proxy(self, client_proxy: ClientProxy):
        with self.__proxy_pool_lock:
            self.__proxy_pool.append(client_proxy)
        self.__loop.call_soon_threadsafe(
            self.__wait_pool_task.set
        )
        logging.info(f"client_proxy_manager: 注册客户端代理：{client_proxy.index}")

    def remove_proxy(self, client_proxy: ClientProxy):
        with self.__proxy_pool_lock:
            self.__proxy_pool.remove(client_proxy)
        client_proxy.stop()
        logging.info(f"client_proxy_manager: 移除客户端代理：{client_proxy.index}")

    def get_client(self, index: int) -> ClientProxy:
        with self.__proxy_pool_lock:
            for client in self.__proxy_pool:
                if client.index == index:
                    return client

    def stop(self):
        self.__stop_clients()
        self.__stop_self()

    def __stop_self(self):
        self.__running.set(False)
        self.__loop.call_soon_threadsafe(
            self.__wait_pool_task.set
        )
        self.__loop.stop()

    def __stop_clients(self):
        for client in self.__proxy_pool:
            self.remove_proxy(client)


ClientProxyManager = ClientProxyManager()
