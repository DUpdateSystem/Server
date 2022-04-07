from getter.hubs.hub_list import hub_dict


def get_single_release(hub_uuid: str, auth: dict or None, app_id: dict) -> list or None:
    return next(get_release_list(hub_uuid, auth, [app_id]))[-1]


def get_release_list(hub_uuid: str, auth: dict or None, app_id_list: list) -> list or None:
    hub = hub_dict[hub_uuid]
    for app_id, release_list in hub.get_release_list(app_id_list, auth):
        yield hub_uuid, auth, app_id, release_list
