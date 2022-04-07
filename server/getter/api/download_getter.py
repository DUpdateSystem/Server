from getter.hubs.hub_list import hub_dict


def get_download_info_list(hub_uuid: str, auth: dict, app_id: list, asset_index: list) -> tuple or None:
    hub = hub_dict[hub_uuid]
    download_info = hub.get_download_info(app_id, asset_index, auth)
    if type(download_info) is str:
        return [{"url": download_info}]
    else:
        return download_info
