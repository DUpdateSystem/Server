from peewee import Model, SqliteDatabase
from playhouse.pool import PooledSqliteDatabase

file_name = 'cache.db'

local_cache_db = PooledSqliteDatabase(file_name, max_connections=32, stale_timeout=300)
local_memory_db = SqliteDatabase('file:temp_database?mode=memory&cache=shared', uri=True)


class BaseMeta:
    database = local_cache_db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = local_cache_db
