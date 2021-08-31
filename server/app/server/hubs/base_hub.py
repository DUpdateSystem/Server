import asyncio
from abc import ABCMeta, abstractmethod

from requests import HTTPError

from app.server.config import server_config
from app.server.hubs.hub_script_utils import http_get, return_value, run_fun_list_without_error
from app.server.manager.data.constant import logging
from app.server.utils.generator_cache import GeneratorCache


class BaseHub(object, metaclass=ABCMeta):
    """ 软件源脚本需要实现的抽象类
    """

    @staticmethod
    @abstractmethod
    def get_uuid() -> str:
        pass

    def init_account(self, account: dict) -> dict or None:
        pass

    async def get_release_list(self, generator_cache: GeneratorCache,
                               app_id_list: list, auth: dict or None = None):
        fun_list = [self.__call_release_list_fun(generator_cache, app_id, auth) for app_id in app_id_list]
        await run_fun_list_without_error(fun_list)

    async def __call_release_list_fun(self, generator_cache: GeneratorCache, app_id: dict, auth: dict or None):
        """ 当软件源未实现 get_release_list 函数时，缺省调用 get_release 函数获取数据的协程函数
        """
        # 获取云端数据
        release_list = None
        # noinspection PyBroadException
        try:
            release_list = self.get_release(app_id, auth)
            # 缓存数据，包括 404 None 数据
        except HTTPError as e:
            status_code = e.response.status_code
            logging.warning(f"""app_id: {app_id}
            HTTP CODE {status_code} ERROR: {e}""")
            if status_code == 404:
                release_list = []
        except asyncio.TimeoutError:
            logging.warning(f'app_id: {app_id} timeout!')
        except Exception:
            debug_mode = server_config.debug_mode
            log = f"app_id: {app_id}"
            if debug_mode:
                log += " \nERROR: "
            else:
                log += " ERROR"
            logging.exception(log, exc_info=debug_mode)
        return_value(generator_cache, app_id, release_list)

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

    async def _get_download_info(self, app_id: dict, asset_index: list,
                                 auth: dict or None = None) -> dict or tuple or None:
        return self.get_download_info(app_id, asset_index, auth)

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
                [{"name": [name]. "url": url, "header": "headers", [headers], "cookies": [cookies]}, ...]
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
        return http_get(self.available_test_url, False).ok

    @property
    def available_test_url(self) -> str:
        return ""

    @staticmethod
    async def __call_fun(core):
        return core()
