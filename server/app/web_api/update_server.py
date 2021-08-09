import json
from uuid import UUID

from flask import Blueprint

from app.server.manager.data_manager import data_manager, WaitingDataError
from .utils import path_to_dict, get_auth

update_server_page = Blueprint('update_server_page', __name__)


@update_server_page.route('/v<int:api_version>/app/<uuid:hub_uuid>/<path:app_id_path>/release')
def get_app_release(api_version: str, hub_uuid: UUID, app_id_path: str):
    if api_version != 1:
        return 'v1 only', 400
    release_list, status = get_app_release_list(api_version, hub_uuid, app_id_path)
    if status == 200:
        return json.loads(release_list)[0], status


@update_server_page.route('/v<int:api_version>/app/<uuid:hub_uuid>/<path:app_id_path>/releases')
def get_app_release_list(api_version: str, hub_uuid: UUID, app_id_path: str):
    if api_version != 1:
        return 'v1 only', 400
    auth = get_auth()
    app_id = path_to_dict(app_id_path)
    try:
        release_list = data_manager.get_release(str(hub_uuid), auth, app_id)
    except WaitingDataError as e:
        return e.process_time, 206
    if release_list:
        return json.dumps(release_list), 200
    elif release_list is not None and not release_list:
        return '', 410
    else:
        return '', 406
