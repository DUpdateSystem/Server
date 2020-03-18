import inspect
import importlib
import pathlib
import glob
from pathlib import PurePath
from .hubs.base_hub import BaseHub
from .hubs.library.hub_list import hub_dict


class HubServerManager:
    """管理软件源
    负责初始化与获取实例"""
    __slots__ = ["hub_class_dict"]

    def __init__(self):
        self.hub_class_dict = hub_dict
        # self.init_hub()

    def init_hub(self):
        """初始化所有软件源到一个字典中"""
        self.hub_class_dict.clear()
        for hub_class in get_all_scipt_class():
            self.hub_class_dict[hub_class.uuid] = hub_class

    def get_hub(self, hub_uuid):
        """通过 UUID 获取软件源实例
        Args:
            hub_uuid: 软件源的 UUID
        Returns:
            BaseHub 实例
        """
        return self.hub_class_dict[hub_uuid]


def get_all_scipt_class():
    current_path = pathlib.Path(__file__).parent.absolute()
    mypath = PurePath(current_path, "./hubs/library")
    onlyfiles = glob.glob(str(mypath) + "/*.py")
    class_list = []
    for file_path in onlyfiles:
        print(file_path)
        module = importlib.import_module(".hubs.library", package='server')
        clsmembers = inspect.getmembers(module, inspect.isclass)
        print(clsmembers)
        for hub in clsmembers:
            if hub is BaseHub:
                class_list.append(hub)
    return class_list
