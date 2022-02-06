import json
from datetime import datetime

from requests import HTTPError

from ..base_hub import BaseHub
from ..hub_script_utils import http_get


class Gitlab(BaseHub):
    """Gitlab 软件源"""

    @staticmethod
    def get_uuid() -> str:
        return '0aacd531-ebac-44d4-92da-5dfcb70e4592'

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        owner_name = app_id['owner']
        repo_name = app_id['repo']
        response = None
        try:
            response = _get_response(owner_name, repo_name)
        except HTTPError as e:
            if e.response.status_code == 404:
                return []
        data = []
        # 分版本号获取信息
        for commit in response:
            release_info = {}
            # 获取名称
            name = f"{_get_timestamp(commit['committed_date'])}({commit['short_id']})"
            # 获取版本号
            release_info["version_number"] = name
            # 获取更新日志与存在于更新日志里的可下载文件
            release_info["change_log"] = commit["message"]
            # 获取下载文件
            assets = [{
                "file_name": "commit web page",
                "download_url": commit['web_url'],
            }]

            release_info["assets"] = assets
            data.append(release_info)
        return data

    @property
    def available_test_url(self) -> str:
        return "https://gitlab.com"


def _get_timestamp(iso_time):
    return datetime.fromisoformat(iso_time).timestamp()


def _get_api_url(owner_name: str, repo_name: str) -> str:
    """获取 Gitlab API 地址（Commit）
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: String
        GitHub API 地址
    """
    return f"https://gitlab.com/api/v4/projects/{owner_name}%2F{repo_name}/repository/commits"


def _get_response(owner_name: str, repo_name: str) -> json:
    """获取 Gitlab API 返回的 JSON 数据
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: JSON
    """
    api_url = _get_api_url(owner_name, repo_name)
    return http_get(api_url).json()
