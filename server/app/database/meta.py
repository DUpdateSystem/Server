from pathlib import Path

from peewee import Model
from playhouse.pool import PooledSqliteDatabase

sql_dir_path = 'data/sql'

Path(sql_dir_path).mkdir(parents=True, exist_ok=True)

main_cache_path = sql_dir_path + '/cache.db'
other_cache_path = sql_dir_path + '/_cache.db'

local_cache_db = PooledSqliteDatabase(main_cache_path, max_connections=32, stale_timeout=300, autoconnect=False)
local_memory_db = PooledSqliteDatabase(other_cache_path, uri=True,
                                       max_connections=64, stale_timeout=300, autoconnect=False)


class BaseMeta:
    database = local_cache_db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = local_cache_db
