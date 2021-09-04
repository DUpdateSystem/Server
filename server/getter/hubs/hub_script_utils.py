import asyncio
import re

from bs4 import BeautifulSoup
from requests import Response, Session, HTTPError

from config import debug_mode
from database.cache_manager import cache_manager
from getter.net_getter.release_getter import get_single_release
from utils.requests import session

android_app_key = 'android_app_package'


def parsing_http_page(url: str, params=None) -> BeautifulSoup:
    """简易包装的获取并解析网页操作
    Args:
        url: 目标网页
        params: 请求头
    Returns:
        由 BeautifulSoup4 解析的网页节点
    """
    headers = {
        'User-Agent': "Mozilla/5.0 (X11; Linux x86_64; rv:67.0) Gecko/20100101 Firefox/67.0"
    }
    html = http_get(url, headers=headers, params=params).text
    return BeautifulSoup(html, "html5lib")


def http_get(url: str, throw_error=True, **kwargs) -> Response or None:
    """简易包装的 get 方法
    Args:
        url: 访问的网址
        **kwargs: Optional arguments that ``request`` takes.
        throw_error: 是否抛出 HTTP 状态码异常
    Returns:
        包装网站响应的 Request 对象
    """
    try:
        response = session.get(url, **kwargs, timeout=15)
        response.raise_for_status()
        return response
    except Exception as e:
        if e is HTTPError:
            raise e
        if throw_error:
            raise e
        return None


def get_session() -> Session:
    """获取默认 Session 对象
    Returns: Session
    """
    return session


def search_version_number_string(string: str or None) -> str or None:
    """在字符串中匹配 x.y.z 版本号
    Args:
        string: 需匹配的字符串
    Returns:
        一个 Match object（详见 re 库）, 若无匹配项则返回 None
    """
    if string is None:
        return None
    pattern = "(\\d+(\\.\\d+)*)(([.|\\-|+|_| ]|[0-9A-Za-z])*)"
    return re.search(pattern, string)


def search_url_string(string: str or None) -> str or None:
    """在字符串中匹配 x.y.z 版本号
    Args:
        string: 需匹配的字符串
    Returns:
        匹配到的 URL
    """
    if string is None:
        return None
    pattern = '((ht|f)tps?:)//[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]'
    return re.search(pattern, string).lastgroup


def get_tmp_cache(key: str) -> bytes or None:
    """获取临时缓存
    Args:
        key: 缓存键值

    Returns:
        缓存的 bytes
    """
    try:
        return cache_manager.get_tmp_cache(key)
    except KeyError:
        return None


def add_tmp_cache(key: str, value: bytes):
    """添加临时缓存
    Args:
        key: 缓存键值
        value: 缓存的字符串
    Returns:
        None
    """
    if value:
        cache_manager.add_tmp_cache(key, value)


def del_tmp_cache(key: str):
    """删除临时缓存
    Args:
        key: 缓存键值
    """
    cache_manager.del_tmp_cache(key)


def get_release_by_uuid(uuid, app_id: dict, auth: dict or None = None, use_cache=True) -> list:
    """获取对应 UUID 的软件源的 get_release 函数的输出
    Args:
        uuid: 软件源的 UUID
        use_cache: 是否使用服务器缓存
        app_id: 客户端上传的软件属性
        auth: 软件源身份验证信息
    Returns:
        对应的下载地址
    """
    return get_single_release(uuid, auth, app_id, use_cache=use_cache)


def get_url_from_release_fun(uuid, app_id: dict, asset_index, auth: dict or None = None, use_cache=True) -> str:
    """获取对应 UUID 的软件源的 get_release 函数输出的下载地址
    Args:
        uuid: 软件源的 UUID
        use_cache: 是否使用服务器缓存
        app_id: 客户端上传的软件属性
        asset_index: 客户端请求的下载文件的索引
        auth: 软件源身份验证信息
    Returns:
        对应的下载地址
    """
    release_list = get_release_by_uuid(uuid, app_id, auth, use_cache)
    release: dict = release_list[asset_index[0]]
    return release["assets"][asset_index[1]]["download_url"]


def get_new_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if debug_mode:
        loop.set_debug(True)
    return loop


def call_def_in_loop_return_result(core, _loop=None):
    if _loop:
        loop = _loop
    else:
        loop = get_new_asyncio_loop()
    try:
        result = loop.run_until_complete(core)
    except RuntimeError:
        future = asyncio.run_coroutine_threadsafe(core, loop)
        result = future.result()
    if not _loop:
        loop.close()
    return result
