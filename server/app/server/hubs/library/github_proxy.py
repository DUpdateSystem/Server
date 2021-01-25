from .github import Github
from ..base_hub import BaseHub
from ..hub_script_utils import get_release_by_uuid


class GithubProxy(BaseHub):
    """GitHub 下载加速源"""
    @staticmethod
    def get_uuid() -> str:
        return '56fca689-47a7-496a-b290-8bd717c06960'

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        base_hub_uuid = Github.get_uuid()
        data = get_release_by_uuid(base_hub_uuid, app_id, auth)
        for release in data:
            for asset in release["assets"]:
                url = asset["download_url"]
                asset["download_url"] = f'https://git.johnsonran.cn/{url}'
                # 使用 johnsonran Github 下载加速服务，感谢 johnsonran
        return data
