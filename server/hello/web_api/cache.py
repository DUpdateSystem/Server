from hashlib import md5
from quart import Quart, request, Request, Response
from database.cache_manager import cache_manager


def regist_cache(app: Quart):
    app.before_request(check_cache)
    app.after_request(set_cache)


def check_cache_hash(path, cache_hash) -> bool:
    return cache_manager.get_tmp_cache(path).decode() == cache_hash


def check_cache():
    try:
        path = request.path
        path_hash = md5(path.encode()).digest()
        cache_hash = request.headers.get("cache_hash")
        if check_cache_hash(path_hash, cache_hash):
            return Request(204)
    except ValueError:
        return


async def set_cache(response: Response):
    path = request.path
    res_data = await response.get_data()
    path_hash = md5(path.encode()).hexdigest()
    cache_hash = md5(res_data).digest()
    cache_manager.add_tmp_cache(path_hash, cache_hash)
    return response
