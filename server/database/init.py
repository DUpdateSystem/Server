from database.model.hub_cache import HubCache
from database.model.release_cache import ReleaseCache
from database.model.temp_cache import TempCache
from .meta import local_cache_db, memory_db


def init_database():
    connect_db(memory_db)
    connect_db(local_cache_db)
    local_cache_db.create_tables([HubCache, ReleaseCache, TempCache])
    close_db(memory_db)
    close_db(local_cache_db)


def connect_db(db):
    db.connect(reuse_if_open=True)


def close_db(db):
    if db.is_connection_usable():
        db.close()
