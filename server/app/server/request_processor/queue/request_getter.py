from .header_key import RELEASE_REQUEST, DOWNLOAD_REQUEST, CLOUD_CONFIG_REQUEST
from app.server.utils.queue import ProcessQueue


class RequestList(ProcessQueue):

    def __add_request(self, key, *args):
        self.put((key, args))

    def add_releases_request(self, hub_uuid: str, auth: dict, app_id: dict, use_cache: bool = True):
        self.__add_request(RELEASE_REQUEST, hub_uuid, auth, app_id, use_cache)

    def add_download_request(self, hub_uuid: str, auth: dict, app_id: list, asset_index: list):
        self.__add_request(DOWNLOAD_REQUEST, hub_uuid, auth, app_id, asset_index)

    def add_cloud_config_request(self, dev_version: bool, migrate_master: bool):
        self.__add_request(CLOUD_CONFIG_REQUEST, dev_version, migrate_master)


request_list = RequestList()
