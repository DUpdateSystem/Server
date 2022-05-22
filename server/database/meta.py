import re

from peewee import Model
from playhouse.pool import PooledMySQLDatabase, PooledSqliteExtDatabase
from playhouse.shortcuts import ThreadSafeDatabaseMetadata

from config import debug_mode

from .config import db_password, db_url

db_user, db_host, db_port = re.split('[@:]', db_url)
db_url.split(':')
db_name = 'upa-data'

memory_db = PooledSqliteExtDatabase(':memory:',
                                    max_connections=2048,
                                    autoconnect=False)
if debug_mode:
    local_cache_db = memory_db
else:
    local_cache_db = PooledMySQLDatabase(db_name,
                                         host=db_host,
                                         port=int(db_port),
                                         user=db_user,
                                         password=db_password,
                                         max_connections=2048,
                                         autoconnect=False)
memory_db = local_cache_db


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
