from bs4 import BeautifulSoup
from utils.json import from_json, to_json

from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, http_get, get_tmp_cache, add_tmp_cache

cache_key = "lsposed_full_module_json"


class LsposedRepo(BaseHub):
    @staticmethod
    def get_uuid() -> str:
        return '401e6259-2eab-46f0-8e8a-d2bfafedf5bf'

    def get_release_list(self, app_id_list: list, auth: dict or None = None):
        try:
            json_data = from_json(get_tmp_cache(cache_key))
        except AttributeError:
            json_data = None
        if not json_data:
            json_data = http_get("https://modules.lsposed.org/modules.json").json()
            if json_data:
                add_tmp_cache(cache_key, to_json(json_data))
        if json_data:
            for app_id in app_id_list:
                yield app_id, self.__get_release(app_id, json_data)

    @staticmethod
    def __get_release(app_id: dict, json_data):
        if android_app_key not in app_id:
            return []
        package = app_id[android_app_key]
        module = None
        for item in json_data:
            if item['name'] == package:
                module = item
                break
        if not module:
            return []
        version_list = module['releases']
        release_list = []
        for version in version_list:
            change_log_raw = version['descriptionHTML']
            if change_log_raw:
                soup = BeautifulSoup(change_log_raw, "html5lib")
                change_log = soup.text
            else:
                change_log = None
            assets = [{
                "file_name": asset['name'],
                "download_url": asset['downloadUrl']
            } for asset in version['releaseAssets']]
            release_info = {
                "version_number": version['name'],
                "change_log": change_log,
                "assets": assets,
            }
            release_list.append(release_info)
        return release_list

    @property
    def available_test_url(self) -> str:
        return "https://modules.lsposed.org"
