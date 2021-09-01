from app.database.model.hub_cache import HubCache
from app.database.model.memory_cache import MemoryCache
from app.database.model.release_cache import ReleaseCache
from .meta import local_cache_db, local_memory_db


def init_database():
    connect_db()
    local_cache_db.create_tables([HubCache, ReleaseCache])
    local_memory_db.create_tables([MemoryCache])
    close_db()


def connect_db():
    if local_cache_db.is_closed():
        local_cache_db.connect()
    if local_memory_db.is_closed():
        local_memory_db.connect()


def close_db():
    if local_cache_db.is_connection_usable():
        local_cache_db.close()
    if local_memory_db.is_connection_usable():
        local_memory_db.close()
