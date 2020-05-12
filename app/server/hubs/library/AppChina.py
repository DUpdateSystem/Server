from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id, parsing_http_page


class FDroid(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        package = _get_package(app_id)

        if package is None:
            return None

        url = _get_url(package)
        soup = parsing_http_page(url)

        newest_version = soup.find(name="div", attrs={
                                   "class": "intro app-other-info-intro"}).find_all(name="p", attrs={"class": "art-content"})[2].text
        newest_changelog = soup.find_all(
            name="p", attrs={"class": "art-content"})[1].text
        newest_downloadurl = soup.find(name="a", attrs={"class": "download_app"})[
            'onclick'].split("\'")[1]

        data = [{
            "version_number": newest_version,
            "change_log": newest_changelog,
            "assets": [{
                "file_name": package + ".apk",
                "download_url": newest_downloadurl
            }]
        }]

        return data


def _get_url(app_package: str) -> str:
    return f"http://www.appchina.com/app/{app_package}"


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
