import os
import sys

import json

from flask import Flask, request, jsonify

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.server.manager.data_manager import data_manager
from app.server.hubs.library.hub_list import hub_dict


class Data:
    def __init__(self):
        self.app = Flask(__name__)
        self.debug_mode = True


data = Data()
app = data.app


@app.route('/v1/<hub_uuid>')
def get_update_by_hub_uuid(hub_uuid: str):
    if hub_uuid not in hub_dict:
        print(f"NO HUB: {hub_uuid}")
        return "", 400
    app_info_list = json.loads(request.headers.get("App-Info-List"))
    return_list = []
    for app_info in app_info_list:
        release_info = None
        try:
            release_info = data_manager.get_release_info(hub_uuid, app_info)
        except Exception as e:
            print("ERROR")
            print(f"app_info: {app_info}")
            print(f"Reason: {e}")
            if data.debug_mode:
                raise e
        return_list.append({
            "app_info": app_info,
            "release_info": release_info
        })
    return jsonify(return_list)


@app.route("/")
def hello():
    return "Hello World from Flask"


def run(debug=True):
    data.debug_mode = debug
    if debug:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', debug=False, port=80)


if __name__ == "__main__":
    run(debug=False)
