import logging as _logging

import colorlog
from config import debug_mode

LOG_FORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"


def __init_logging():
    if debug_mode:
        logger = _logging.getLogger()
    else:
        logger = _logging.getLogger(__name__)
    logger.setLevel(_logging.DEBUG)
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(LOG_FORMAT))
    logger.addHandler(handler)
    return logger


logging = __init_logging()
