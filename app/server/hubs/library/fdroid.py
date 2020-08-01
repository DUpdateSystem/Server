from xml.etree import ElementTree

from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id, http_get, get_tmp_cache, add_tmp_cache, raise_no_app_error


class FDroid(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        package, language = _get_key(app_id)
        if package is None:
            return None
        url = 'https://f-droid.org/repo'
        tree = _get_xml_tree(url)
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


def _get_url(app_package: str, language: str or None) -> str:
    if language:
        return f"https://f-droid.org/{language}/packages/{app_package}/"
    else:
        return f"https://f-droid.org/packages/{app_package}"


def _get_key(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package"), \
           get_value_from_app_id(app_info, "language")
