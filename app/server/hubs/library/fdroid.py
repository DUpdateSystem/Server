from ..base_hub import BaseHub
from ..hub_script_utils import get_value_from_app_info, parsing_http_page


class FDroid(BaseHub):
    def get_release_info(self, app_info: list) -> list or None:
        package = self.__get_package(app_info)
        if package is None:
            return None
        url = self.__get_url(package)
        soup = parsing_http_page(url)
        version_number_list = [item.a["name"] for item in soup.find_all(class_="package-version-header")]
        newest_changelog_div = soup.find(class_="package-whats-new")
        newest_changelog = None
        if newest_changelog_div is not None:
            newest_changelog = ""
            for text in [text for text in newest_changelog_div.stripped_strings]:
                newest_changelog += f"\n{text}"
        download_list = soup.find_all(class_="package-version-download")
        download_url_list = [tag.find(href=True)["href"] for tag in download_list]
        download_file_name_list = []
        for download_url in download_url_list:
            i = download_url.rfind("/") + 1
            download_file_name_list.append(download_url[i:])
        data = []
        for i in range(len(version_number_list)):
            release_info = {"version_number": version_number_list[i]}
            if i == 0 and newest_changelog is not None:
                release_info["change_log"] = newest_changelog
            assets = [{
                "file_name": download_file_name_list[i],
                "download_url": download_url_list[i]
            }]
            release_info["assets"] = assets
            data.append(release_info)
        return data

    @staticmethod
    def __get_url(app_package: str) -> str:
        return f"https://f-droid.org/packages/{app_package}"

    @staticmethod
    def __get_package(app_info: list) -> str or None:
        return get_value_from_app_info(app_info, "android_app_package")
