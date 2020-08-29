import os
from pathlib import Path, PurePath
import configparser
from distutils.util import strtobool


class _ServerConfig:
    def __init__(self, config_path: str or None = None):
        self.host = "localhost"
        self.port = 5000
        self.max_workers = 16
        self.debug_mode = True
        self.auto_refresh_time = 6
        self.cloud_rule_hub_url = ""
        self.download_asset_host = "localhost"
        self.download_asset_dir_path = self.__parse_file_path()
        self.use_cache_db = False
        self.redis_server_address = "localhost"
        self.redis_server_port = 6379
        self.redis_server_password = ""
        if config_path:
            self.init_config_file(config_path)

    def init_config_file(self, file_path: str):
        config = configparser.ConfigParser()
        config.read(file_path)
        base_config = config['base']
        self.host = base_config['Host']
        self.port = int(base_config['Port'])
        self.max_workers = int(base_config['MaxWorkers'])
        self.debug_mode = bool(strtobool(base_config['DebugMode']))
        data_config = config['data']
        self.auto_refresh_time = int(data_config['AutoRefreshTime'])
        self.cloud_rule_hub_url = data_config['CloudRuleHubUrl']
        self.download_asset_host = data_config['DownloadAssetHost']
        self.download_asset_dir_path = self.__parse_file_path(data_config['DownloadAssetDirPath'])
        cache_db_config = config['cache_db']
        self.use_cache_db = bool(strtobool(cache_db_config['UseCacheDB']))
        self.redis_server_address = cache_db_config['RedisServerAddress']
        self.redis_server_port = int(cache_db_config['RedisServerPort'])
        self.redis_server_password = cache_db_config['RedisServerPassword']

    @staticmethod
    def __parse_file_path(path: str = None) -> Path:
        if not path:
            pure_path = PurePath(os.getcwd(), 'asset')
        else:
            app_work_dir_identifier = '$APP'
            if app_work_dir_identifier in path and path.index(app_work_dir_identifier) == 0:
                subdirectory = path.replace(app_work_dir_identifier, '.')
                pure_path = PurePath(os.getcwd(), subdirectory)
            else:
                pure_path = PurePath(path)
        return Path(pure_path)


server_config = _ServerConfig("./config.ini")
