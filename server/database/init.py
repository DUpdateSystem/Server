from database.model.hub_cache import HubCache
from database.model.memory_cache import TempCache
from database.model.release_cache import ReleaseCache
from .meta import local_cache_db


def init_database():
    connect_db()
    local_cache_db.create_tables([HubCache, ReleaseCache, TempCache])
    close_db()


def connect_db():
    if local_cache_db.is_closed():
        local_cache_db.connect()


def close_db():
    if local_cache_db.is_connection_usable():
        local_cache_db.close()
