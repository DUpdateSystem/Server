from utils.logging import logging

from database.cache_manager import cache_manager


def check_hub_available(hub) -> bool:
    key = f"{hub.get_uuid()} available_test"
    cache = cache_manager.get_tmp_cache(key)
    if cache:
        available = bool(cache)
    else:
        available = hub.available_test()
        cache_manager.add_tmp_cache(key, available)
    if not available:
        logging.warning(f"hub not available: {hub.get_uuid()}")
    return available
