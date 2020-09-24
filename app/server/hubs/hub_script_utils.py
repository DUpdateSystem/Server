import re
import tarfile
import tempfile
from io import BytesIO

from bs4 import BeautifulSoup
from requests import Response, Session, HTTPError

from app.server.manager.cache_manager import cache_manager
from app.server.manager.data.constant import session as __session, proxies as __proxies
from app.server.manager.data.generator_cache import GeneratorCache

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
        response = __session.get(url, **kwargs, proxies=__proxies, timeout=15)
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
    return __session


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


def get_tmp_cache(key: str) -> str or None:
    """获取临时缓存
    Args:
        key: 缓存键值

    Returns:
        缓存的字符串
    """
    try:
        raw = cache_manager.get_tmp_cache(key)
    except KeyError:
        return None
    with tempfile.TemporaryFile(mode='w+b') as f:
        f.write(raw)
        f.flush()
        f.seek(0)
        # noinspection PyTypeChecker
        with tarfile.open(fileobj=f, mode='r:xz') as tar:
            with tar.extractfile("1.txt") as file:
                return file.read()


def add_tmp_cache(key: str, value: str):
    """获取临时缓存
    Args:
        key: 缓存键值
        value: 缓存的字符串
    Returns:
        None
    """
    if value:
        out = BytesIO()
        with tarfile.open(mode="w:xz", fileobj=out) as tar:
            data = value.encode('utf-8')
            file = BytesIO(data)
            info = tarfile.TarInfo(name="1.txt")
            info.size = len(data)
            tar.addfile(tarinfo=info, fileobj=file)

        cache_manager.add_tmp_cache(key, out.getvalue())


def return_value(generator_cache: GeneratorCache, app_id: dict, value):
    generator_cache.add_value({"id": app_id, "v": value})


def raise_no_app_error():
    response = Response()
    response.status_code = 404
    raise HTTPError(response=response)
