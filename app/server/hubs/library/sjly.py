from bs4 import BeautifulSoup

from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id, get_response


class Sjly(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        app_id = _get_app_id(app_id)
        if app_id is None:
            return None
        url = _get_url(app_id)
        response = get_response(url, verify=False)
        response.encoding = 'utf-8'
        html = response.text
        soup = BeautifulSoup(html, "html5lib")
        version_number_elements = soup.find_all(name="strong")
        version_row_string_list = [element.a.text for element in version_number_elements if element.a]
        version_number_list = [item[item.find('v') + 1:] for item in version_row_string_list]
        newest_changelog_mark_elements = soup.find(class_="Lef1_cent").find_next(name="h3", class_="biaoti",
                                                                                     text="更新说明")
        newest_changelog = None
        if newest_changelog_mark_elements is not None:
            newest_changelog = newest_changelog_mark_elements.next_element.next_element.next_element.text
        download_url_elements = soup.find_all(name="span", class_="bdown")
        download_url_list = [element.a['href'] for element in download_url_elements]
        data = []
        for i in range(len(version_number_list)):
            release_info = {"version_number": version_number_list[i]}
            if i == 0 and newest_changelog:
                release_info["change_log"] = newest_changelog
            assets = [{
                "file_name": f"{app_id}_{version_row_string_list[i]}.apk",
                "download_url": download_url_list[i]
            }]
            release_info["assets"] = assets
            data.append(release_info)
        return data


def _get_url(app_id: str) -> str:
    return f"https://soft.shouji.com.cn/down/{app_id}.html"


def _get_app_id(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "app_id")
