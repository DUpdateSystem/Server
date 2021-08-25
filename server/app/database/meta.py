from peewee import Model
from playhouse.pool import PooledSqliteDatabase

file_name = 'cache.db'

db = PooledSqliteDatabase(file_name, max_connections=32, stale_timeout=300)


class BaseMeta:
    database = db


class BaseModel(Model):
    class Meta(BaseMeta):
        database = db
