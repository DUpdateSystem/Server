import re

import requests
from bs4 import BeautifulSoup


def parsing_http_page(url: str) -> BeautifulSoup:
    """简易包装获取并解析网页操作
    Args:
        url: 目标网页
    Returns:
        由 BeautifulSoup4 解析的网页节点
    """
    html = get_response_string(url)
    return BeautifulSoup(html, "html5lib")


def get_response_string(url: str, payload=None) -> str:
    """简易包装 get 方法
    Args:
        url: 访问的网址
        payload: 请求头
    Returns:
        网站的响应主体
    """
    response = requests.get(url, params=payload)
    response.raise_for_status()
    return response.text


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


def get_value_from_app_info(app_info: list, key: str) -> str or None:
    """获取 app_info 中的值
    Args:
        app_info: 应用信息列表
        key: 搜索的键
    Returns:
        搜索到的键值，若没有相关键则返回 None
    """
    for i in app_info:
        if i.key == key:
            return i.value
    return None
