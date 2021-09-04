import gzip
import logging
import tempfile
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, http_get, get_tmp_cache, add_tmp_cache

cache_key = "xposed_full_module_xml"


class XpModRepo(BaseHub):
    @staticmethod
    def get_uuid() -> str:
        return 'e02a95a2-af76-426c-9702-c4c39a01f891'

    async def get_release_list(self, app_id_list: list, auth: dict or None = None):
        xml_str = get_tmp_cache(cache_key)
        if not xml_str:
            raw_str = http_get("https://dl-xda.xposed.info/repo/full.xml.gz", stream=True).raw.data
            xml_str = _raw_to_xml_string(raw_str)
            if xml_str:
                add_tmp_cache(cache_key, xml_str)
        if xml_str:
            try:
                tree = ElementTree.fromstring(xml_str)
            except Exception as e:
                logging.error(e)
                raise RuntimeError
            for app_id in app_id_list:
                yield app_id, self.__get_release(app_id, tree)

    @staticmethod
    def __get_release(app_id: dict, tree):
        if android_app_key not in app_id:
            return []
        package = app_id[android_app_key]
        module = tree.find(f'.//module[@package="{package}"]')
        if not module:
            return []
        version_list = module.findall('version')
        release_list = []
        for version in version_list:
            download_url = version.find('download').text
            file_name = download_url[download_url.rfind('/') + 1:]
            change_log_raw = version.find('changelog').text
            if change_log_raw:
                soup = BeautifulSoup(change_log_raw, "html5lib")
                change_log = soup.text
            else:
                change_log = None
            release_info = {
                "version_number": version.find('name').text,
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
        return "https://dl-xda.xposed.info"


def _raw_to_xml_string(raw):
    with tempfile.TemporaryFile(mode='w+b') as f:
        f.write(raw)
        f.flush()
        f.seek(0)
        with gzip.GzipFile(mode='r', fileobj=f) as gzip_file:
            return gzip_file.read().decode("utf-8")
