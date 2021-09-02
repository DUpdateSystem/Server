import asyncio
import logging

from config import debug_mode
from getter.hubs.hub_list import hub_dict


async def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
    try:
        hub = hub_dict[hub_uuid]
    except KeyError:
        return None
    if hub_uuid not in hub_dict:
        logging.warning(f"NO HUB: {hub_uuid}")
        raise KeyError
    try:
        download_info = await __run_download_core(hub, auth, app_id, asset_index)
        if type(download_info) is str:
            return [{"url": download_info}]
        else:
            return download_info
    except Exception as e:
        logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=debug_mode)
        return e


async def __run_download_core(hub, auth: dict, app_id: list, asset_index: list):
    aw = None
    try:
        # noinspection PyProtectedMember
        aw = hub._get_download_info(app_id, asset_index, auth)
        download_info = await asyncio.wait_for(aw, timeout=20)
        return download_info
    except asyncio.TimeoutError:
        logging.info(f'aw: {aw} timeout!')
