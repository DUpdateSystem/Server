from peewee import Model
from playhouse.pool import PooledMySQLDatabase

cache_name = 'cache'

local_cache_db = PooledMySQLDatabase(cache_name, host='localhost', user='upa',
                                     max_connections=1024, stale_timeout=5, autoconnect=False)


class BaseMeta:
    database = local_cache_db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = local_cache_db
