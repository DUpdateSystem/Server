from time import time

from peewee import *

from database.meta import BaseModel, BaseMeta


class TempCache(BaseModel):
    class Meta(BaseMeta):
        db_table = 'temp_cache'

    key = CharField(primary_key=True)
    value = CharField()
    timestamp = IntegerField(null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_timestamp()

    def update_timestamp(self):
        self.timestamp = time()
