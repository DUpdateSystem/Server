from .ask_proxy_error import NeedClientProxy
from .http_request_item import HttpRequestItem
from .http_request_body import HttpRequestBody


def proxy_get(url: str, headers: dict or None = None):
    """简易包装的客户端代理 get 方法
    Args:
        url: 访问的网址
        headers: 请求头参数字典
    Returns:
        抛出包含请求数据的请求代理对象的错误
    """
    http_request_item = HttpRequestItem("post", url, headers)
    raise NeedClientProxy(http_request_item)


def proxy_post(url: str, headers: dict or None = None,
               body_type: str or None = None, body_text: str or None = None):
    """简易包装的客户端代理 post 方法
    Args:
        url: 访问的网址
        headers: 请求头参数字典
        body_type: 请求主体数据类型
        body_text: 请求主体
    Returns:
        抛出包含请求数据的请求代理对象的错误
    """
    post_body = HttpRequestBody(body_type, body_text)
    http_request_item = HttpRequestItem("post", url, headers, post_body)
    raise NeedClientProxy(http_request_item)
