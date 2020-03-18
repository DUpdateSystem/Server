from flask import Flask, request
import json
from .hub_server_manager import HubServerManager

app = Flask(__name__)
hub_server_manager = HubServerManager()


@app.route('/v1/<hub_uuid>')
def get_update_by_hub_uuid(hub_uuid):
    hub = hub_server_manager.get_hub(hub_uuid)
    app_info_list = json.loads(request.headers.get("app_info_list"))
    return_dict = {}
    for app_info in app_info_list:
        app_id = str(app_info)
        return_dict[app_id] = hub.get_release_info(app_info)
    return json.dumps(return_dict)


if __name__ == '__main__':
    app.run()
