import re

import requests
from bs4 import BeautifulSoup
from requests import Request, Session

__session = requests.Session()


def parsing_http_page(url: str, payload=None) -> BeautifulSoup:
    """简易包装的获取并解析网页操作
    Args:
        url: 目标网页
        payload: 请求头
    Returns:
        由 BeautifulSoup4 解析的网页节点
    """
    html = get_response(url, payload=payload).text
    return BeautifulSoup(html, "html5lib")


def get_response(url: str, payload=None, throw_error=True) -> Request or None:
    """简易包装的 get 方法
    Args:
        url: 访问的网址
        payload: 请求头
        throw_error: 是否抛出 HTTP 状态码异常
    Returns:
        包装网站响应的 Request 对象
    """
    try:
        response = __session.get(url, params=payload, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        if e is requests.HTTPError:
            raise e
        if throw_error:
            raise e
        return None


def get_session() -> Session:
    """获取默认 Session 对象
    Returns: Session
    """
    return __session


def search_version_number_string(string: str or None) -> str or None:
    """在字符串中匹配 x.y.z 版本号
    Args:
        string: 需匹配的字符串
    Returns:
        匹配到的版本号
    """
    if string is None:
        return None
    pattern = "(\\d+(\\.\\d+)*)(([.|\\-|+|_| ]|[0-9A-Za-z])*)"
    return re.search(pattern, string)


def get_value_from_app_id(app_id: list, key: str) -> str or None:
    """获取 app_id 中的值
    Args:
        app_id: 应用信息列表
        key: 搜索的键
    Returns:
        搜索到的键值，若没有符合的键则返回 None
    """
    for i in app_id:
        if i["key"] == key:
            return i["value"]
    return None
