from database.model.hub_cache import HubCache
from database.model.release_cache import ReleaseCache
from database.model.temp_cache import TempCache
from .meta import local_cache_db


def init_database():
    connect_db()
    local_cache_db.create_tables([HubCache, ReleaseCache, TempCache])
    close_db()


def connect_db():
    local_cache_db.connect(reuse_if_open=True)


def close_db():
    if local_cache_db.is_connection_usable():
        local_cache_db.close()
