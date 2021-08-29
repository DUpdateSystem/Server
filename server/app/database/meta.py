from peewee import Model
from playhouse.pool import PooledSqliteDatabase

file_name = 'cache.db'

local_cache_db = PooledSqliteDatabase(file_name, max_connections=32, stale_timeout=300)
local_memory_db = PooledSqliteDatabase('file:temp_database?mode=memory&cache=shared', uri=True,
                                       max_connections=32, stale_timeout=300)


class BaseMeta:
    database = local_cache_db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = local_cache_db
