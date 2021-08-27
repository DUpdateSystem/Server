from urllib.parse import urlparse

from .github import Github
from ..hub_script_utils import get_release_by_uuid


class GithubProxy(Github):
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
                asset["download_url"] = self.__get_proxy_url(url)
                # Github 下载加速服务，感谢 JohnsonRan 的发现与 FastGit UK 提供下载服务.
                # FastGit UK 文档/捐赠：https://doc.fastgit.org/zh-cn/#%E5%85%B3%E4%BA%8E-fastgit
        return data

    @staticmethod
    def __get_proxy_url(old_url: str) -> str:
        parsed = urlparse(old_url)
        replaced = parsed._replace(netloc='download.fastgit.org')
        return replaced.geturl()
