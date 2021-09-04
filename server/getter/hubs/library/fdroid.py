from xml.etree import ElementTree

from database.utils.zip import unzip_raw
from utils.logging import logging
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, http_get, get_tmp_cache, add_tmp_cache


class FDroid(BaseHub):
    @staticmethod
    def get_uuid() -> str:
        return '6a6d590b-1809-41bf-8ce3-7e3f6c8da945'

    def get_release_list(self, app_id_list: list, auth: dict or None = None):
        if auth and 'repo_url' in auth:
            repo_url = auth["repo_url"]
        else:
            repo_url = 'https://f-droid.org/repo'
        try:
            tree = _get_xml_tree(repo_url)
        except Exception as e:
            logging.error(e)
            raise RuntimeError
        for app_id in app_id_list:
            yield app_id, self.__get_release(app_id, tree, repo_url)

    @staticmethod
    def __get_release(app_id: dict, tree, url):
        if android_app_key not in app_id:
            return []
        package = app_id[android_app_key]
        module = tree.find(f'.//application[@id="{package}"]')
        if not module:
            return []
        changelog_item = module.find('changelog')
        newest_changelog = None
        if changelog_item:
            newest_changelog = changelog_item.text
        packages = module.findall('package')
        release_list = []
        for i in range(len(packages)):
            version = packages[i]
            file_name = version.find('apkname').text
            download_url = f'{url}/{file_name}'
            if i == 0:
                change_log = newest_changelog
            else:
                change_log = None
            release_info = {
                "version_number": version.find('version').text,
                "change_log": change_log,
                "assets": [{
                    "file_name": file_name,
                    "download_url": download_url
                }]
            }
            release_list.append(release_info)
        return release_list

    @property
    def available_test_url(self) -> str:
        return "https://f-droid.org/"


def _get_xml_tree(url: str = 'https://f-droid.org/repo'):
    try:
        xml_raw = get_tmp_cache(url)
    except KeyError:
        xml_raw = None
    if not xml_raw:
        xml_raw = http_get(f'{url}/index.xml', stream=True).text
        if xml_raw:
            add_tmp_cache(url, xml_raw)
    xml_string = unzip_raw(xml_raw, "1.txt")
    return ElementTree.fromstring(xml_string)
