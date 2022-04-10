from database.model.hub_cache import HubCache
from database.model.release_cache import ReleaseCache
from database.model.tmp_cache import TmpCache
from .meta import local_cache_db, memory_db


def init_database():
    connect_db(memory_db)
    memory_db.create_tables([TmpCache])
    close_db(memory_db)

    connect_db(local_cache_db)
    local_cache_db.create_tables([HubCache, ReleaseCache])
    close_db(local_cache_db)


def connect_db(db):
    db.connect(reuse_if_open=True)


def close_db(db):
    if db.is_connection_usable():
        db.close()
