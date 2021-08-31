from pathlib import Path

from peewee import Model
from playhouse.pool import PooledSqliteDatabase

sql_dir_path = 'data/sql'

Path(sql_dir_path).mkdir(parents=True, exist_ok=True)

file_name = sql_dir_path + '/cache.db'

local_cache_db = PooledSqliteDatabase(file_name, max_connections=32, stale_timeout=300, autoconnect=False)
local_memory_db = PooledSqliteDatabase('file:temp_database?mode=memory&cache=shared', uri=True,
                                       max_connections=64, stale_timeout=300, autoconnect=False)


class BaseMeta:
    database = local_cache_db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = local_cache_db
