from app.database.model.hub_cache import HubCache
from app.database.model.memory_cache import MemoryCache
from .meta import local_cache_db, local_memory_db
from app.database.model.release_cache import ReleaseCache


def init_database():
    local_cache_db.connect()
    local_cache_db.create_tables([HubCache, ReleaseCache])
    local_memory_db.connect()
    local_memory_db.create_tables([MemoryCache])
