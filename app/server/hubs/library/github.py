import json
from ..base_hub import BaseHub
from ..hub_script_utils import get_response_string, search_version_number_string


class Github(BaseHub):
    """GitHub 软件源"""

    def get_release_info(self, app_info: list) -> list or None:
        owner_name, repo_name = _get_base_info(app_info)
        if repo_name is None or owner_name is None:
            return
        response = _get_response(owner_name, repo_name)
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


def _get_base_info(app_info: list) -> tuple:
    """从 app_info 获取作者名称与仓库名称
    Arg:
        app_info: 客户端上传的信息
    Return:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
     """
    owner_name = None
    repo_name = None
    for i in app_info:
        key = i.key
        value = i.value
        if key == "owner":
            owner_name = value
        elif key == "repo":
            repo_name = value

    return owner_name, repo_name


def _get_api_url(owner_name: str, repo_name: str) -> str:
    """获取 GitHub API 地址
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: String
        GitHub API 地址
    """
    return "https://api.github.com/repos/" \
           + owner_name + "/" \
           + repo_name + "/releases"


def _get_response(owner_name: str, repo_name: str) -> json:
    """获取 GitHub API 返回的 JSON 数据
    Arg:
        owner_name: 所有者名称
        repo_name: Git 仓库名称
    Return: JSON
    """
    api_url = _get_api_url(owner_name, repo_name)
    response_string = get_response_string(api_url)
    return json.loads(response_string)
