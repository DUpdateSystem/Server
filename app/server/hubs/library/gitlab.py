import json

from bs4 import BeautifulSoup

from .github import _get_base_info
from ..base_hub import BaseHub
from ..hub_script_utils import http_get


class Gitlab(BaseHub):
    """Gitlab 软件源"""

    def get_release_info(self, app_id: list) -> tuple or None:
        owner_name, repo_name = _get_base_info(app_id)
        if repo_name is None or owner_name is None:
            return
        response = _get_response(owner_name, repo_name)
        data = []
        # 分版本号获取信息
        for release in response:
            release_info = {}
            # 获取名称
            name = release["name"]
            # 获取版本号
            release_info["version_number"] = name
            # 获取更新日志
            description_html = release["description_html"]
            soup = BeautifulSoup(description_html, "html5lib")
            release_info["change_log"] = soup.text
            # 获取下载文件
            link_list = soup.find_all(name='a')
            assets = []
            for item in link_list:
                url = item["href"]
                if url[0] == '/':
                    url = "https://gitlab.com" + url
                asset_info = {
                    "file_name": item.text,
                    "download_url": url
                }
                assets.append(asset_info)
            release_info["assets"] = assets
            data.append(release_info)
        return data


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
