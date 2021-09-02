import json

from bs4 import BeautifulSoup

from ..base_hub import BaseHub
from ..hub_script_utils import http_get


class Gitlab(BaseHub):
    """Gitlab 软件源"""

    @staticmethod
    def get_uuid() -> str:
        return 'a84e2fbe-1478-4db5-80ae-75d00454c7eb'

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        owner_name = app_id['owner']
        repo_name = app_id['repo']
        response = _get_response(owner_name, repo_name)
        data = []
        # 分版本号获取信息
        for release in response:
            release_info = {}
            # 获取名称
            name = release["name"]
            # 获取版本号
            release_info["version_number"] = name
            assets = []
            # 获取更新日志与存在于更新日志里的可下载文件
            if "description_html" in release:
                description_html = release["description_html"]
                soup = BeautifulSoup(description_html, "html5lib")
                release_info["change_log"] = soup.text
                link_list = soup.find_all(name='a')
                for item in link_list:
                    url = item["href"]
                    if url[0] == '/':
                        url = "https://gitlab.com" + url
                    asset_info = {
                        "file_name": item.text,
                        "download_url": url
                    }
                    assets.append(asset_info)
            elif "description" in release:
                release_info["change_log"] = release["description"]
            else:
                release_info["change_log"] = None
            # 获取下载文件
            try:
                for raw_asset in release["assets"]["links"]:
                    asset_info = {
                        "file_name": raw_asset["name"],
                        "download_url": raw_asset["url"]
                    }
                    assets.append(asset_info)
            except KeyError:
                pass

            release_info["assets"] = assets
            data.append(release_info)
        return data

    @property
    def available_test_url(self) -> str:
        return "https://gitlab.com"


def _get_api_url(owner_name: str, repo_name: str) -> str:
    """获取 Gitlab API 地址
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: String
        GitHub API 地址
    """
    return f"https://gitlab.com/api/v4/projects/{owner_name}%2F{repo_name}/releases"


def _get_response(owner_name: str, repo_name: str) -> json:
    """获取 Gitlab API 返回的 JSON 数据
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: JSON
    """
    api_url = _get_api_url(owner_name, repo_name)
    return http_get(api_url).json()
