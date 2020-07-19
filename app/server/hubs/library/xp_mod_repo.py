import gzip
import tempfile
from xml.etree import ElementTree

from bs4 import BeautifulSoup

from ..base_hub import BaseHub
from ..hub_script_utils import http_get, get_value_from_app_id, raise_no_app_error
from ...manager.cache_manager import cache_manager

cache_key = "xposed_full_module_xml_file_bytes"


class XpModRepo(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        package = _get_package(app_id)
        if package is None:
            return None
        raw = None
        try:
            raw = cache_manager.get_tmp_cache(cache_key)
        except KeyError:
            pass
        if not raw:
            raw = http_get("https://dl-xda.xposed.info/repo/full.xml.gz", stream=True).raw.data
            if raw:
                cache_manager.add_tmp_cache(cache_key, raw)
        with tempfile.TemporaryFile(mode='w+b') as f:
            f.write(raw)
            f.flush()
            f.seek(0)
            with gzip.GzipFile(mode='r', fileobj=f) as gzip_file:
                tree = ElementTree.parse(gzip_file)
        module = tree.find(f'.//module[@package="{package}"]')
        if not module:
            raise_no_app_error()
        version_list = module.findall('version')
        data = []
        for i in range(len(version_list)):
            version = version_list[i]
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


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
