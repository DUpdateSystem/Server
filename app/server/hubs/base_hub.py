from abc import ABCMeta, abstractmethod


class BaseHub(metaclass=ABCMeta):
    """ 软件源脚本需要实现的抽象类
    """

    @abstractmethod
    def get_release_info(self, app_id: list) -> tuple or None:
        """获取更新版本信息
        Args:
            app_id: 客户端上传的软件属性
                example:
                [
                    {key : "", value : ""}
                    {key : "", value : ""}
                ]

        Return: JSON
            example:
            [{
                version_number: "",
                change_log: "",
                assets: [{ name: "", download_url: "", file_type: "" }]
            }]
        """
        pass

    def get_download_info(self, app_id: list, asset_index: list) -> dict or None:
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
