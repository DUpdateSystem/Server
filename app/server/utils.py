import logging

from colorlog import ColoredFormatter
from requests import Response

from .hubs import hub_script_utils

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"


def init_logging():
    logging.root.setLevel(LOG_LEVEL)
    formatter = ColoredFormatter(LOG_FORMAT)
    stream = logging.StreamHandler()
    stream.setLevel(LOG_LEVEL)
    stream.setFormatter(formatter)
    log = logging.getLogger('base_logger')
    log.setLevel(LOG_LEVEL)
    log.addHandler(stream)
    return log


def get_response(url: str, throw_error=False, **kwargs) -> Response or None:
    return hub_script_utils.get_response(url, throw_error, **kwargs)


logging = init_logging()
