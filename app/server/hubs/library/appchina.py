from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_id, parsing_http_page, search_version_number_string


class AppChina(BaseHub):
    def get_release_info(self, app_id: list) -> tuple or None:
        package = _get_package(app_id)

        if package is None:
            return None

        url = _get_url(package)
        soup = parsing_http_page(url)

        newest_version = soup.find(name="div", attrs={
            "class": "intro app-other-info-intro"}).find_all(name="p", attrs={"class": "art-content"})[2].text
        row_version_number_list = [newest_version] + [item.text for item in
                                                      soup.find_all(class_='history-verison-app-versionName')]

        version_number_list = [search_version_number_string(item).group(0) for item in row_version_number_list]
        changelog_div = [soup.find_all(
            name="p", attrs={"class": "art-content"})[1]] + soup.find_all(
            class_='history-version-app-updateMsg')
        changelog = [item.text for item in changelog_div]
        newest_download_url = soup.find(name="a", attrs={"class": "download_app"})['onclick'].split("\'")[1]

        download_url_list = [newest_download_url] + [item["href"] for item in soup.find_all(name="a",
                                                                                            class_='historyVerison-download fright download_app')]
        data = []
        for i in range(len(version_number_list)):
            release_info = {"version_number": version_number_list[i],
                            "change_log": changelog[i]}
            assets = [{
                "file_name": package + ".apk",
                "download_url": download_url_list[i]
            }]
            release_info["assets"] = assets
            data.append(release_info)
        return data


def _get_url(app_package: str) -> str:
    return f"http://www.appchina.com/app/{app_package}"


def _get_package(app_info: list) -> str or None:
    return get_value_from_app_id(app_info, "android_app_package")
