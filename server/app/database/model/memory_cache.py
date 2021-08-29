from time import time

from peewee import *

from app.database.meta import local_memory_db


class MemoryCache(Model):
    class Meta:
        database = local_memory_db
        db_table = 'cache'

    key = TextField(primary_key=True)
    value = TextField()
    timestamp = IntegerField(null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_timestamp()

    def update_timestamp(self):
        self.timestamp = time()
