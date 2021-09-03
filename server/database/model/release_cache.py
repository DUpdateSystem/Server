from time import time

from peewee import *

from .hub_cache import HubCache
from ..field.text import LongTextField
from ..meta import BaseModel, BaseMeta
from ..utils import from_json, to_json


class ReleaseCache(BaseModel):
    class Meta(BaseMeta):
        db_table = 'cache_release'
        indexes = (
            (('hub_pair_id', 'app_id'), True),
        )

    hub_info = ForeignKeyField(HubCache, column_name='hub_pair_id', backref='hub_info')
    app_id_str = CharField(column_name='app_id')
    __release = LongTextField(null=True, default=None, column_name='release')
    timestamp = IntegerField(null=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_timestamp()

    def update_timestamp(self):
        self.timestamp = time()

    @property
    def app_id(self):
        return from_json(self.app_id_str)

    @app_id.setter
    def app_id(self, value):
        self.app_id_str = to_json(value)

    @property
    def release(self):
        release = from_json(self.__release)
        if release is not None:
            return release
        else:
            return []

    @release.setter
    def release(self, value):
        if value:
            self.__release = to_json(value)
