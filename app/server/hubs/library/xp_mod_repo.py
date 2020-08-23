import gzip
import tempfile
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from app.server.utils import call_fun_list_in_loop, call_async_fun_with_id
from ..base_hub import BaseHub
from ..hub_script_utils import http_get, get_value_from_app_id, get_tmp_cache, add_tmp_cache, raise_no_app_error

cache_key = "xposed_full_module_xml"


class XpModRepo(BaseHub):
    def get_release_list(self, app_id_list: list, auth: dict or None = None) -> dict or None:
        xml_str = get_tmp_cache(cache_key)
        if not xml_str:
            raw_str = http_get("https://dl-xda.xposed.info/repo/full.xml.gz", stream=True).raw.data
            xml_str = _raw_to_xml_string(raw_str)
            if xml_str:
                add_tmp_cache(cache_key, xml_str)
        if xml_str:
            tree = ElementTree.fromstring(xml_str)
            fun_list = [call_async_fun_with_id(app_id, lambda: self.__get_release(app_id['android_app_package'], tree))
                        for app_id in app_id_list if 'android_app_package' in app_id]
            data_list = call_fun_list_in_loop(fun_list)
            return {frozenset(key): value for key, value in data_list}

    @staticmethod
    def __get_release(package: str, tree) -> tuple or None:
        module = tree.find(f'.//module[@package="{package}"]')
        if not module:
            raise_no_app_error()
        version_list = module.findall('version')
        data = []
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
            data.append(release_info)
        return data


def _raw_to_xml_string(raw):
    with tempfile.TemporaryFile(mode='w+b') as f:
        f.write(raw)
        f.flush()
        f.seek(0)
        with gzip.GzipFile(mode='r', fileobj=f) as gzip_file:
            return gzip_file.read().decode("utf-8")


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
