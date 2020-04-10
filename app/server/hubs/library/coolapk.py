import re

from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_info, parsing_http_page


class CoolApk(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        package = self.__get_package(app_id)
        if package is None:
            return None
        url = self.__get_url(package)
        soup = parsing_http_page(url)
        version_number = soup.find(class_="list_app_info").get_text("|", strip=True)
        newest_changelog_div = soup.find(class_="apk_left_title_info")
        newest_changelog = None
        if newest_changelog_div is not None:
            newest_changelog = ""
            for text in [text for text in newest_changelog_div.stripped_strings]:
                newest_changelog += f"\n{text}"
        javascript = soup.find("script", type="text/javascript").text
        pattern = '"(.*?)"'
        release_download = re.search(pattern, javascript).group(0)[1:-1]
        data = [{
            "version_number": version_number,
            "change_log": newest_changelog,
            "assets": [{
                "file_name": package + ".apk",
                "download_url": release_download
            }]
        }]
        return data

    @staticmethod
    def __get_url(app_package: str) -> str:
        return f"https://www.coolapk.com/apk/{app_package}"

    @staticmethod
    def __get_package(app_info: list) -> str or None:
        return get_value_from_app_info(app_info, "android_app_package")
