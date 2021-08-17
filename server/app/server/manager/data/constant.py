import logging as _logging

import requests
import colorlog

from app.server.config import server_config

proxies = {
    'http': server_config.network_proxy,
    'https': server_config.network_proxy
}

session = requests.Session()

LOG_FORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"


def __init_logging():
    if server_config.debug_mode:
        logger = _logging.getLogger()
    else:
        logger = _logging.getLogger(__name__)
    logger.setLevel(_logging.DEBUG)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger


logging = __init_logging()
