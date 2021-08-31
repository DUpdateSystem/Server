from xml.etree import ElementTree

from app.server.utils.queue import ThreadQueue
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, http_get, get_tmp_cache, add_tmp_cache, return_value, \
    run_fun_list_without_error


class FDroid(BaseHub):
    @staticmethod
    def get_uuid() -> str:
        return '6a6d590b-1809-41bf-8ce3-7e3f6c8da945'

    async def get_release_list(self, generator_cache: ThreadQueue,
                               app_id_list: list, auth: dict or None = None):
        if auth and 'repo_url' in auth:
            repo_url = auth["repo_url"]
        else:
            repo_url = 'https://f-droid.org/repo'
        tree = _get_xml_tree(repo_url)
        fun_list = [self.__get_release(generator_cache, app_id, tree, repo_url) for app_id in app_id_list]
        await run_fun_list_without_error(fun_list)

    @staticmethod
    async def __get_release(generator_cache: ThreadQueue, app_id: dict, tree, url):
        if android_app_key not in app_id:
            return_value(generator_cache, app_id, [])
        package = app_id[android_app_key]
        module = tree.find(f'.//application[@id="{package}"]')
        if not module:
            return_value(generator_cache, app_id, [])
        changelog_item = module.find('changelog')
        newest_changelog = None
        if changelog_item:
            newest_changelog = changelog_item.text
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
        return_value(generator_cache, app_id, data)

    @property
    def available_test_url(self) -> str:
        return "https://f-droid.org/"


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
