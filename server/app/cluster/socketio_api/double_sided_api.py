from app.server.manager.data_manager import data_manager
from app.cluster.manager.finder import get_node_reliability_dict


# noinspection PyMethodMayBeStatic
class DoubleSidedApi:
    async def on_self_get_available_hub(self):
        return data_manager.get_reliability_hub_dict()

    async def on_node_get_reliability_dict(self):
        return get_node_reliability_dict()

    async def on_hub_get_app_release_list(self, hub_uuid: str, auth: dict or None, app_id: dict):
        return data_manager.get_release(hub_uuid, auth, app_id)

    async def on_hub_get_app_download_list(self, hub_uuid: str, auth: dict or None, app_id: dict, asset_index: list):
        return data_manager.get_download_info_list(hub_uuid, auth, app_id, asset_index)
