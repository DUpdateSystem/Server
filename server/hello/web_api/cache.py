from hashlib import md5
from quart import Quart, request, Response
from database.cache_manager import cache_manager


def regist_cache(app: Quart):
    app.before_request(check_cache)
    app.after_request(set_cache)


def cache_key() -> str | None:
    if request.blueprint != "update_server_page" or request.headers.get("Authorization"):
        return None
    return md5(request.path.encode()).hexdigest()


def check_cache():
    key = cache_key()
    cache_hash = request.headers.get("cache_hash")
    if key and cache_hash:
        cached = cache_manager.get_tmp_cache(key)
        if cached is not None and cached.hex() == cache_hash:
            return "", 204


async def set_cache(response: Response):
    key = cache_key()
    if key and response.status_code == 200:
        cache_manager.add_tmp_cache(key, md5(await response.get_data()).digest())
    return response
