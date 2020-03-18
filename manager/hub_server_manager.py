from ..hubs.library.hub_list import hub_dict


class HubServerManager:
    """管理软件源
    负责初始化与获取实例"""
    __slots__ = ["hub_class_dict"]

    def __init__(self):
        self.hub_class_dict = hub_dict

    def get_hub(self, hub_uuid):
        """通过 UUID 获取软件源实例
        Args:
            hub_uuid: 软件源的 UUID
        Returns:
            BaseHub 实例
        """
        return self.hub_class_dict[hub_uuid]
