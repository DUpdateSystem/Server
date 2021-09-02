from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, get_session

_headers = {
    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 10; ONEPLUS A6013 Build/QQ2A.200501.001.B2)"
}


class AppChina(BaseHub):

    @staticmethod
    def get_uuid() -> str:
        return '4a23c3a5-8200-40bb-b961-c1bb5d7fd921'

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        package = app_id[android_app_key]
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

    def available_test_url(self) -> str:
        return "https://mobile.appchina.com/"


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
    return session.post(url=api_url, headers=_headers, data=format_json, timeout=15).json()
