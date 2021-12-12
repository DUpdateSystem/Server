import asyncio

from getter.hubs.hub_list import hub_dict
from getter.net_getter.hub_checker import check_hub_available
from utils.logging import logging


async def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
    try:
        hub = hub_dict[hub_uuid]
    except KeyError:
        return None
    if hub_uuid not in hub_dict:
        logging.warning(f"NO HUB: {hub_uuid}")
        raise KeyError
    try:
        if not check_hub_available(hub):
            return None
        download_info = await __run_download_core(hub, auth, app_id, asset_index)
        if type(download_info) is str:
            return [{"url": download_info}]
        else:
            return download_info
    except Exception as e:
        logging.exception(e)
        return None


async def __run_download_core(hub, auth: dict, app_id: list, asset_index: list):
    aw = None
    try:
        # noinspection PyProtectedMember
        aw = _run_core(hub.get_download_info, app_id, asset_index, auth)
        download_info = await asyncio.wait_for(aw, timeout=20)
        return download_info
    except asyncio.TimeoutError:
        logging.info(f'aw: {aw} timeout!')


async def _run_core(core, *args):
    return core(*args)
