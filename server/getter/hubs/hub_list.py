from app.status_checker.status import __hub_available_key_list
from .base_hub import BaseHub

hub_dict = dict((hub.get_uuid(), hub()) for hub in BaseHub.__subclasses__())

__hub_available_key_list += list(hub_dict.keys())
