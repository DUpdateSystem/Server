from abc import ABCMeta

from requests import HTTPError

from app.server.config import server_config
from app.server.utils import logging, call_fun_list_in_loop, call_async_fun_with_id, get_manager_dict


class BaseHub(metaclass=ABCMeta):
    """ 软件源脚本需要实现的抽象类
    """

    def init_account(self, account: dict) -> dict or None:
        pass

    def get_release_list(self, app_id_list: list, auth: dict or None = None) -> dict or None:
        data_dict = get_manager_dict()
        fun_list = [call_async_fun_with_id(app_id, lambda: self.__call_release_list_fun(data_dict, app_id, auth))
                    for app_id in app_id_list]
        call_fun_list_in_loop(fun_list)
        return data_dict

    def get_release(self, app_id: dict, auth: dict or None = None) -> tuple or None:
        """获取更新版本信息
        Args:
            app_id: 客户端上传的软件属性
                Example: {
                    "user": "",
                    "repo": "",
                }
            auth: 软件源身份验证信息

        Return: tuple
            Keyword Args:
                 app_id (frozenset)
            value:
                有用的信息: tuple
                无用但是需要告知客户端的信息（不存在的软件）: empty tuple
                无用的信息（信息获取失败）: [None, ]
            Example:
            [{
                version_number: "",
                change_log: "",
                assets: [{ file_name: "", download_url: "", file_type: "" }]
            }]
        """
        pass

    def get_download_info(self, app_id: dict, asset_index: list, auth: dict or None = None) -> tuple or None:
        """即时获取下载地址
        Args:
            app_id: 客户端上传的软件属性
            asset_index: 客户端请求的下载文件的索引
                Example: [0, 0] 第一个版本的第一个文件
            auth: 软件源身份验证信息

        Returns: tuple
            Examples:
                (({url}, {request_header_dict}), ...)
                可包含多个下载目标（为了同时下载/安装可能的依赖软件，例如：obb 文件）
                request_header_dict 结构示例: {
                        "<请求头>": "<请求头参数>"
                }
        """
        pass

    def __call_release_list_fun(self, data_dict: dict, app_id: dict, auth: dict or None):
        """
        当软件源未实现 get_release_list 函数时，缺省调用 get_release 函数获取数据的协程函数
        """
        # 获取云端数据
        release_list = [None, ]
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
        except Exception:
            logging.error(f"""app_id: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
        data_dict[frozenset(app_id)] = release_list
