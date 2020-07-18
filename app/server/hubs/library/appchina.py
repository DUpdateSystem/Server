from json import loads

from app.server.utils import get_manager_dict
from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id, proxy_post

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; ONEPLUS A6013 Build/QQ2A.200501.001.B2)",
    "Content-Type": "application/x-www-form-urlencoded"
}
tmp_dict = get_manager_dict()


class AppChina(BaseHub):
    def get_release_info(self, app_id: list):
        package = _get_package(app_id)

        if package is None:
            return None
        newest_json = {"type": "app.detailInfo", "packagename": package}
        _send_api(newest_json)

    @staticmethod
    def get_release_info_1(app_id: list, response_text: str):
        history_json = {"type": "app.pastdetails", "id": 0, "packagename": "com.example.app"}
        package = _get_package(app_id)
        release_info = _get_release(loads(response_text))
        data_json = [release_info]
        tmp_dict[str(app_id)] = data_json
        history_json["packagename"] = package
        _send_api(history_json)

    @staticmethod
    def get_release_info_2(app_id: list, response_text: str) -> tuple or None:
        response_json = loads(response_text)
        data_json = tmp_dict.pop(str(app_id))
        for i in response_json["list"]:
            release_info = _get_release(i)
            data_json.append(release_info)
        return data_json


def _get_release(raw_dict: dict) -> dict:
    return {
        "version_number": raw_dict["versionName"],
        "change_log": raw_dict["updateMsg"],
        "assets": [{
            "file_name": raw_dict["packageName"] + ".apk",
            "download_url": raw_dict["apkUrl"]
        }]
    }


def _send_api(param: dict):
    api_url = "https://mobile.appchina.com/market/api"
    format_json = {"param": str(param), "api": "market.MarketAPI", "\n": ""}
    proxy_post(url=api_url, headers=headers, body_type='multipart/form-data',
               body_text=str(format_json))


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
