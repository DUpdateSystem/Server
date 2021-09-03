from .base_hub import BaseHub

hub_dict = dict((hub.get_uuid(), hub()) for hub in BaseHub.__subclasses__())
