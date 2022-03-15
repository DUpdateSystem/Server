import asyncio

from utils.logging import logging


async def run_with_time_limit(aw, timeout: int, enable_log=True):
    try:
        return await asyncio.wait_for(aw, timeout=timeout)
    except asyncio.TimeoutError:
        if enable_log:
            logging.info(f'aw: {aw} timeout!')
