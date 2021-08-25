from .hub_cache import HubCache
from .meta import db
from .release_cache import ReleaseCache


def init_database():
    db.connect()
    db.create_tables([HubCache, ReleaseCache])
