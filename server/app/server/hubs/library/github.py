import json
import time

from ..base_hub import BaseHub
from ..hub_script_utils import http_get, search_version_number_string


class Github(BaseHub):
    """GitHub 软件源"""

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        owner_name = app_id['owner']
        repo_name = app_id['repo']
        response = _get_response(owner_name, repo_name)
        response.sort(key=_extract_time, reverse=True)
        data = []
        # 分版本号获取信息
        for release in response:
            release_info = {}
            # 获取名称
            name = release["name"]
            if search_version_number_string(name) is None:
                name = release["tag_name"]
            # 获取版本号
            release_info["version_number"] = name
            # 获取更新日志
            release_info["change_log"] = release["body"]
            # 获取下载文件
            assets = []
            for asset in release["assets"]:
                asset_info = {
                    "file_name": asset["name"],
                    "download_url": asset["browser_download_url"],
                    "file_type": asset["content_type"]
                }
                assets.append(asset_info)
            release_info["assets"] = assets
            data.append(release_info)
        return data


def _get_api_url(owner_name: str, repo_name: str) -> str:
    """获取 GitHub API 地址
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: String
        GitHub API 地址
    """
    return f"https://api.github.com/repos/{owner_name}/{repo_name}/releases"


def _get_response(owner_name: str, repo_name: str) -> json:
    """获取 GitHub API 返回的 JSON 数据
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: JSON
    """
    api_url = _get_api_url(owner_name, repo_name)
    return http_get(api_url).json()


def _extract_time(j):
    time_str = j['created_at']
    return time.mktime(time.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ"))
