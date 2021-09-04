import json
from uuid import UUID

import zmq
from flask import Blueprint, Response

from proxy.format.zmq_request_format import dump_release_request, dump_download_request, dump_cloud_config_request
from utils.logging import logging
from .utils import path_to_dict, path_to_int_list, get_auth
from ..zmq_context import context

update_server_page = Blueprint('update_server_page', __name__)

proxy_url = 'tcp://upa-proxy:5559'


@update_server_page.route('/v<int:api_version>/rules/download/<string:config_version>')
def get_cloud_config(api_version: str, config_version: str):
    if api_version != 1:
        return 'v1 only', 400
    if config_version == "master":
        dev_version = False
    elif config_version == "dev":
        dev_version = True
    else:
        return f"wrong config version: {config_version}", 400

    socket = context.socket(zmq.REQ)
    socket.connect(proxy_url)
    mq_request = dump_cloud_config_request(dev_version, True)
    socket.send_string(mq_request)
    cloud_config = socket.recv()
    socket.close()

    if cloud_config:
        return json.loads(cloud_config), 200
    else:
        return '', 404


@update_server_page.route('/v<int:api_version>/app/<uuid:hub_uuid>/<path:app_id_path>/release')
def get_app_release(api_version: str, hub_uuid: UUID, app_id_path: str):
    if api_version != 1:
        return 'v1 only', 400
    logging.debug(f"get_app_release: {hub_uuid}, {app_id_path}")
    response, status = __get_app_release_list(hub_uuid, app_id_path)
    if status == 200:
        return response[0], status
    else:
        return response, status


@update_server_page.route('/v<int:api_version>/app/<uuid:hub_uuid>/<path:app_id_path>/releases')
def get_app_release_list(api_version: str, hub_uuid: UUID, app_id_path: str):
    if api_version != 1:
        return 'v1 only', 400
    logging.debug(f"get_app_release_list: {hub_uuid}, {app_id_path}")
    value, status = __get_app_release_list(hub_uuid, app_id_path)
    if status:
        return Response(json.dumps(value), mimetype='application/json')
    else:
        return value, status


def __get_app_release_list(hub_uuid: UUID, app_id_path: str):
    auth = get_auth()
    app_id = path_to_dict(app_id_path)
    socket = context.socket(zmq.REQ)
    socket.connect(proxy_url)
    mq_request = dump_release_request(str(hub_uuid), auth, app_id, True)
    print(mq_request)
    socket.send_string(mq_request)
    release_list_str = socket.recv()
    socket.close()
    try:
        release_list = json.loads(release_list_str)
    except KeyError:
        return f'no hub: {hub_uuid}', 400
    if release_list:
        return release_list, 200
    elif release_list is not None and not release_list:
        return '', 410
    else:
        return '', 406


@update_server_page.route(
    '/v<int:api_version>/app/<uuid:hub_uuid>/<path:app_id_path>/extra_download/<path:asset_index_path>')
def get_extra_download_info_list(api_version: str, hub_uuid: UUID, app_id_path: str, asset_index_path: str):
    if api_version != 1:
        return 'v1 only', 400
    try:
        asset_index = path_to_int_list(asset_index_path)
    except ValueError:
        return f"wrong index format: {asset_index_path}", 400
    logging.debug(f"get_extra_download_info_list: {hub_uuid}, {app_id_path}, {asset_index_path}")
    auth = get_auth()
    app_id = path_to_dict(app_id_path)
    socket = context.socket(zmq.REQ)
    socket.connect(proxy_url)
    mq_request = dump_download_request(str(hub_uuid), auth, app_id, asset_index)
    socket.send_string(mq_request)
    download_info_list_str = socket.recv()
    socket.close()
    try:
        download_info_list = json.loads(download_info_list_str)
    except KeyError:
        return f'no hub: {hub_uuid}', 400
    if download_info_list:
        return json.dumps(download_info_list), 200
    elif download_info_list is not None and not download_info_list:
        return '', 410
    else:
        return '', 406
