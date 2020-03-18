from abc import ABCMeta, abstractmethod


class BaseHub(metaclass=ABCMeta):
    """ 软件源脚本需要实现的抽象类
    """

    @property
    @abstractmethod
    def uuid(self):
        pass

    @abstractmethod
    def get_release_info(self, app_info):
        """获取更新版本信息
        Args:
            app_info: 客户端上传的信息
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
