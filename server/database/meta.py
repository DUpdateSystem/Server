import re

from peewee import Model
from playhouse.pool import PooledMySQLDatabase, PooledSqliteDatabase
from playhouse.shortcuts import ThreadSafeDatabaseMetadata

from config import db_url, db_password
from config import debug_mode

db_user, db_host, db_port = re.split('[@:]', db_url)
db_url.split(':')
db_name = 'upa-data'

local_cache_db = PooledMySQLDatabase(db_name, host=db_host, port=int(db_port), user=db_user, password=db_password,
                                     stale_timeout=300, max_connections=2048, autoconnect=True)

memory_db = PooledSqliteDatabase(':memory:')
if debug_mode:
    local_cache_db = memory_db


class BaseMemoryMeta:
    database = memory_db


class BaseMemoryModel(Model):
    class Meta(BaseMemoryMeta):
        database = memory_db
        # Instruct peewee to use our thread-safe metadata implementation.
        model_metadata_class = ThreadSafeDatabaseMetadata


class BaseMeta:
    database = local_cache_db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = local_cache_db
        # Instruct peewee to use our thread-safe metadata implementation.
        model_metadata_class = ThreadSafeDatabaseMetadata
