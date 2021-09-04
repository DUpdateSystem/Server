from peewee import *

from ..meta import BaseModel, BaseMeta
from ..utils.json import from_json, to_json


class HubCache(BaseModel):
    class Meta(BaseMeta):
        db_table = 'cache_hub'
        indexes = (
            (('hub_uuid', 'auth'), True),
        )

    pair_id = AutoField(column_name='pair_id')
    hub_uuid = UUIDField(column_name='hub_uuid')
    auth_str = CharField(null=True, default=None, column_name='auth')

    @property
    def auth(self):
        return from_json(self.auth_str)

    @auth.setter
    def auth(self, value):
        self.auth_str = to_json(value)
