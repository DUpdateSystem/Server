from ..base_hub import BaseHub
from ..hub_script_utils import http_get


class ZLiveOfficial(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        data = http_get(_get_url()).json()
        return [{
            "version_number": data["version_name"],
            "change_log": data["changelog"],
            "assets": [{
                "file_name": f'zlive_{data["version_name"]}.apk',
                "download_url": data["url"]
            }]
        }]


def _get_url() -> str:
    return "https://zlive.linroid.com/api/app_version"
