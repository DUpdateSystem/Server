from .github import Github
from ..base_hub import BaseHub


class GithubProxy(Github, BaseHub):
    """GitHub 下载加速源"""
    @staticmethod
    def get_uuid() -> str:
        return '56fca689-47a7-496a-b290-8bd717c06960'

    def get_release(self, app_id: dict, auth: dict or None = None) -> list:
        data = super().get_release(app_id, auth)
        for release in data:
            for asset in release["assets"]:
                url = asset["download_url"]
                asset["download_url"] = f'https://git.johnsonran.cn/{url}'
        return data
