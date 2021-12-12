from database.cache_manager import cache_manager
from getter.hubs.hub_list import hub_dict


def check_hub_available(hub_uuid: str) -> bool:
    hub = hub_dict[hub_uuid]
    key = f"{hub.get_uuid()} available_test"
    cache = cache_manager.get_tmp_cache(key)
    if cache:
        return bool(cache)
    else:
        available_test = hub.available_test()
        cache_manager.add_tmp_cache(key, available_test)
        return available_test
