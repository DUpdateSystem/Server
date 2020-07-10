import asyncio
import logging

from colorlog import ColoredFormatter
from requests import Response

from app.server.hubs import hub_script_utils

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
    return hub_script_utils.http_get(url, throw_error, **kwargs)


def set_new_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_debug(True)
    return loop


def call_def_in_loop_return_result(core, loop):
    try:
        return loop.run_until_complete(core)
    except RuntimeError:
        future = asyncio.run_coroutine_threadsafe(core, loop)
    return future.result()


def call_def_in_loop(core, loop):
    try:
        loop.run_until_complete(core)
    except RuntimeError:
        asyncio.run_coroutine_threadsafe(core, loop)


logging = init_logging()
