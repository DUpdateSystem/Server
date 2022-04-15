from time import time

from peewee import CharField, IntegerField

from ..field.blob import LongBlogField
from ..meta import BaseMemoryModel, BaseMemoryMeta


class TmpCache(BaseMemoryModel):

    class Meta(BaseMemoryMeta):
        db_table = 'cache_tmp'

    key = CharField(primary_key=True, column_name='key')
    value = LongBlogField(column_name='value')
    timestamp = IntegerField(null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_timestamp()

    def update_timestamp(self):
        self.timestamp = time()
