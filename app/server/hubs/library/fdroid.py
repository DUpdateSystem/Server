from xml.etree import ElementTree

from app.server.utils import call_fun_list_in_loop, call_async_fun_with_id
from ..base_hub import BaseHub
from ..hub_script_utils import http_get, get_tmp_cache, add_tmp_cache, raise_no_app_error


class FDroid(BaseHub):
    def get_release_list(self, app_id_list: list, auth: dict or None = None) -> dict or None:
        if auth and 'repo_url' in auth:
            repo_url = auth["repo_url"]
        else:
            repo_url = 'https://f-droid.org/repo'
        tree = _get_xml_tree(repo_url)
        fun_list = [
            call_async_fun_with_id(app_id, lambda: self.__get_release(app_id['android_app_package'], tree, repo_url))
            for app_id in app_id_list if 'android_app_package' in app_id]
        data_list = call_fun_list_in_loop(fun_list)
        return {frozenset(key): value for key, value in data_list}

    @staticmethod
    def __get_release(package: str, tree, url) -> tuple or None:
        module = tree.find(f'.//application[@id="{package}"]')
        if not module:
            raise_no_app_error()
        newest_changelog = module.find('changelog').text
        packages = module.findall('package')
        data = []
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
            data.append(release_info)
        return data


def _get_xml_tree(url: str = 'https://f-droid.org/repo'):
    xml_string = None
    try:
        xml_string = get_tmp_cache(url)
    except KeyError:
        pass
    if not xml_string:
        xml_string = http_get(f'{url}/index.xml', stream=True).text
        if xml_string:
            add_tmp_cache(url, xml_string)
    return ElementTree.fromstring(xml_string)
