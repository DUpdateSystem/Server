from .getter import web_getter_manager
from .getter_request import WebGetterRequest

from app.server.manager.data.generator_cache import ProcessGeneratorCache


def send_getter_request(hub_uuid: str, app_id_list: list, auth: dict or None = None,
                        use_cache: bool = True, cache_data: bool = True) -> ProcessGeneratorCache:
    request = WebGetterRequest(hub_uuid, app_id_list, auth, use_cache, cache_data)
    web_getter_manager.send_request(request)
    return request.queue
