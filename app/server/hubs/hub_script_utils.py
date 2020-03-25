import requests
import re


def get_response_string(url: str, payload=None):
    """简易包装 get 方法
    Args:
        url: 访问的网址
        payload: 请求头
    Returns:
        网站的响应主体
    """
    return requests.get(url, params=payload).text


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
