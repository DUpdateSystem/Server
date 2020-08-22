from abc import ABCMeta

from requests import HTTPError

from app.config import server_config
from app.server.utils import logging, call_fun_list_in_loop


class BaseHub(metaclass=ABCMeta):
    """ 软件源脚本需要实现的抽象类
    """

    def init_account(self, account_id: dict) -> dict or None:
        pass

    def get_release_list(self, app_id_list: list, auth: dict or None = None) -> dict or None:
        fun_list = [lambda: (app_id, self.__call_release_list_fun(app_id, auth)) for app_id in app_id_list]
        data_list = call_fun_list_in_loop(fun_list)
        return {key: value for key, value in data_list}

    # noinspection PyMethodMayBeStatic
    def get_release(self, app_id: dict, auth: dict or None = None) -> tuple or None:
        """获取更新版本信息
        Args:
            app_id: 客户端上传的软件属性
                example:
                {
                    "user": "",
                    "repo": "",
                }
            auth: 软件源身份验证信息

        Return: JSON
            example:
            [{
                version_number: "",
                change_log: "",
                assets: [{ name: "", download_url: "", file_type: "" }]
            }]
        """
        return []

    def get_download_info(self, app_id: dict, asset_index: list) -> dict or None:
        """即时获取下载地址
        Args:
            app_id: 客户端上传的软件属性
            asset_index: 客户端请求的下载文件的索引
                example: [0, 0] 第一个版本的第一个文件

        Returns: JSON
            Examples:
                {
                    url: "",
                    request_header : {
                        "<请求头>": "<请求头参数>"
                    }
                }
        """
        pass

    def __call_release_list_fun(self, app_id: dict, auth: dict or None = None) -> tuple or None:
        """
        Args:
            app_id: 客户端上传的软件属性
            auth: 软件源身份验证信息

        Returns:
            有用的信息: tuple
            无用但是需要告知客户端的信息（不存在的软件）: empty tuple
            无用的信息（信息获取失败）: [None, ]
        """
        # 获取云端数据
        release_list = [None, ]
        # noinspection PyBroadException
        try:
            release_list = self.get_release(app_id, auth)
            # 缓存数据，包括 404 None 数据
        except HTTPError as e:
            status_code = e.response.status_code
            logging.warning(f"""app_info: {app_id}
            HTTP CODE {status_code} ERROR: {e}""")
            if status_code == 404:
                release_list = []
            else:
                raise e
        except Exception:
            logging.error(f"""app_info: {app_id} \nERROR: """, exc_info=server_config.debug_mode)
        return release_list
