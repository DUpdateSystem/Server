import asyncio

from utils.logging import logging


async def run_with_time_limit(aw, timeout: int):
    try:
        await asyncio.wait_for(aw, timeout=timeout)
    except asyncio.TimeoutError:
        logging.info(f'aw: {aw} timeout!')
