from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id, get_session

headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; ONEPLUS A6013 Build/QQ2A.200501.001.B2)"
}


class AppChina(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        package = _get_package(app_id)

        if package is None:
            return None

        newest_json = {"type": "app.detailInfo", "packagename": "com.example.app"}
        history_json = {"type": "app.pastdetails", "id": 0, "packagename": "com.example.app"}

        data_json = []
        newest_json["packagename"] = package
        response_json = _send_api(newest_json)
        release_info = _get_release(response_json)
        data_json.append(release_info)
        history_json["packagename"] = package
        response_json = _send_api(history_json)
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


def _send_api(param: dict) -> dict:
    session = get_session()
    api_url = "https://mobile.appchina.com/market/api"
    format_json = {"param": str(param), "api": "market.MarketAPI", "\n": ""}
    return session.post(url=api_url, headers=headers, data=format_json).json()


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
