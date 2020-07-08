import asyncio
import random

from requests import HTTPError

from app.server.utils import set_new_asyncio_loop
from .client_proxy import ClientProxy
from .data import get_manager_value, get_manager_list


class ClientProxyManager:
    __loop = set_new_asyncio_loop()
    __wait_pool_task = asyncio.Event()
    __proxy_pool = get_manager_list()
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
        # 检查代理池
        if not self.__proxy_pool:
            self.__loop.run_until_complete(
                self.__wait_pool_task.wait()
            )
        else:
            self.__loop.call_soon_threadsafe(
                self.__wait_pool_task.clear
            )
        # 检查运行状态
        if not self.__running.value:
            raise KeyboardInterrupt
        # 向客户端发送代理请求
        client_proxy: ClientProxy = random.choice(self.__proxy_pool)
        response = client_proxy.http_request(method, url, headers, body_type, body_text)
        # 检查 HTTP 数据
        status_code = response["code"]
        if status_code < 200 or status_code >= 400:
            raise HTTPError()
        return response["text"]

    def add_proxy(self, client_proxy: ClientProxy):
        self.__proxy_pool.append(client_proxy)
        self.__loop.call_soon_threadsafe(
            self.__wait_pool_task.set
        )

    def remove_proxy(self, client_proxy: ClientProxy):
        self.__proxy_pool.remove(client_proxy)

    def get_client(self, index: int) -> ClientProxy:
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

    def __stop_clients(self):
        for client in self.__proxy_pool:
            client.stop()


ClientProxyManager = ClientProxyManager()
