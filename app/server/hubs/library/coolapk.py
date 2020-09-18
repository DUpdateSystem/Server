import re

from requests import HTTPError

from app.server.manager.data.constant import logging
from ..base_hub import BaseHub
from ..hub_script_utils import android_app_key, parsing_http_page, get_session, raise_no_app_error


class CoolApk(BaseHub):
    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        package = app_id[android_app_key]
        if package == 'android':
            raise_no_app_error()
        url = _get_url(package)
        soup = parsing_http_page(url)
        # noinspection PyArgumentList
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
        raw_download_url = get_session().head(release_download, allow_redirects=True).url
        data = [{
            "version_number": version_number,
            "change_log": newest_changelog,
            "assets": [{
                "file_name": package + ".apk",
                "download_url": raw_download_url
            }]
        }]
        return data

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> tuple or None:
        from app.server.manager.data_manager import data_manager
        from app.server.hubs.hub_list import hub_dict
        hub_uuid = None
        for uuid in hub_dict:
            if self is hub_dict[uuid]:
                hub_uuid = uuid
                break
        release_dict = next(data_manager.get_release_dict(hub_uuid, [app_id], auth))
        release_list = next(iter(release_dict.values()))
        download_url = release_list[asset_index[0]]["assets"][asset_index[1]]["download_url"]
        try:
            get_session().head(download_url).raise_for_status()
            logging.debug("网址验证正确")
        except HTTPError:
            logging.debug("网址错误，尝试重新获取")
            release_list = data_manager.get_release_list(hub_uuid, app_id, use_cache=False)["app_status"]
            download_url = release_list[asset_index[0]]["assets"][asset_index[1]]["download_url"]
        return (download_url,),


def _get_url(app_package: str) -> str:
    return f"https://www.coolapk.com/apk/{app_package}"
