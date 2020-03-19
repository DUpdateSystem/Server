from flask import Flask, request
import json
from .manager.data_manager import data_manager, tl

app = Flask(__name__)


@app.route('/v1/<hub_uuid>')
def get_update_by_hub_uuid(hub_uuid: str):
    app_info_list = json.loads(request.headers.get("app_info_list"))
    return_dict = {}
    for app_info in app_info_list:
        app_id = str(app_info)
        return_dict[app_id] = data_manager.get_release_info(hub_uuid, app_info)
    return json.dumps(return_dict)


def main():
    tl.start()
    app.run()


if __name__ == '__main__':
    main()
