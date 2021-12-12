from abc import ABCMeta, abstractmethod

from getter.hubs.hub_script_utils import http_get


class BaseHub(object, metaclass=ABCMeta):
    """ 软件源脚本需要实现的抽象类
    """

    @staticmethod
    @abstractmethod
    def get_uuid() -> str:
        pass

    def get_release_list(self, app_id_list: list, auth: dict or None = None):
        for app_id in app_id_list:
            yield app_id, self.get_release(app_id, auth)

    def get_release(self, app_id: dict, auth: dict or None = None) -> list or None:
        """获取更新版本信息
        Args:
            app_id: 客户端上传的软件属性
                Example: {
                    "user": "",
                    "repo": "",
                }
            auth: 软件源身份验证信息

        Return: list
            有效数据: list
            无效但是需要告知客户端的信息（不存在的软件）: empty tuple
            无效且无用的数据（信息获取失败）: None
            Example: [{
                version_number: "",
                change_log: "",
                assets: [{ file_name: "", download_url: "", file_type: "" }]
            }]
        """
        pass

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> dict or tuple or None:
        """即时获取下载地址
        Args:
            app_id: 客户端上传的软件属性
            asset_index: 客户端请求的下载文件的索引
                Example: [0, 0] 第一个版本的第一个文件
            auth: 软件源身份验证信息

        Returns: tuple
            Examples:
                [url]
                or
                [{"name": [name]. "url": [url], "header": [header dict], "cookies": [cookies]}, ...]
                可包含多个下载目标（为了同时下载/安装可能的依赖软件，例如：obb 文件）
                request_header_dict 结构示例: {
                        "<请求头>": "<请求头参数>"
                }
        """
        pass

    # noinspection PyMethodMayBeStatic
    def available_test(self) -> bool:
        """可用性测试
        Returns: bool
         软件源的源站是否可以连接
        """
        # noinspection PyBroadException
        try:
            return http_get(self.available_test_url, False).ok
        except Exception:
            return False

    @property
    def available_test_url(self) -> str:
        return ""

    @staticmethod
    async def __call_fun(core):
        return core()
