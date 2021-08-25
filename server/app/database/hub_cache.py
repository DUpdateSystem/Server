from peewee import *

from .meta import BaseModel, BaseMeta
from .utils import from_json, to_json


class HubCache(BaseModel):
    class Meta(BaseMeta):
        db_table = 'hub_cache'
        indexes = (
            (('hub_uuid', 'auth'), True),
        )

    pair_id = AutoField()
    hub_uuid = UUIDField()
    auth_str = TextField(null=True, default=None, column_name='auth')

    @property
    def auth(self):
        return from_json(self.auth_str)

    @auth.setter
    def auth(self, value):
        self.auth_str = to_json(value)
