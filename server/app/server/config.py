import configparser
import os
from distutils.util import strtobool
from pathlib import Path, PurePath


class _ServerConfig:
    def __init__(self, config_path: str or None = None):
        self.host = "localhost"
        self.port = 5255
        self.cluster_port = self.port + 1
        self.max_workers = 16
        self.debug_mode = True
        self.auto_refresh_time = 6
        self.network_timeout = 15
        self.cloud_rule_hub_url = ""
        self.download_asset_host = "localhost"
        self.download_asset_dir_path = self.__parse_file_path()
        self.use_cache_db = False
        self.redis_node_list = [{"host": "localhost", "port": 6379}]
        self.redis_server_password = None
        self.network_proxy = None
        if config_path:
            self.init_config_file(config_path)

    def init_config_file(self, file_path: str):
        config = configparser.ConfigParser()
        config.read(file_path)
        base_config = config['base']
        self.host = base_config['Host']
        self.port = int(base_config['Port'])
        self.cluster_port = int(base_config['ClusterPort'])
        self.max_workers = int(base_config['MaxWorkers'])
        self.debug_mode = bool(strtobool(base_config['DebugMode']))
        data_config = config['data']
        self.auto_refresh_time = int(data_config['AutoRefreshTime'])
        self.cloud_rule_hub_url = data_config['CloudRuleHubUrl']
        self.download_asset_host = data_config['DownloadAssetHost']
        self.download_asset_dir_path = self.__parse_file_path(data_config['DownloadAssetDirPath'])
        self.network_timeout = int(data_config['NetworkTimeout'])
        cache_db_config = config['cache_db']
        self.use_cache_db = bool(strtobool(cache_db_config['UseCacheDB']))
        self.__parse_redis_config(cache_db_config)

    def __parse_redis_config(self, cache_db_config):
        redis_host_list = cache_db_config['RedisServerUrl'].split()
        self.redis_server_password = cache_db_config['RedisServerPassword']
        self.redis_node_list.clear()
        for url in redis_host_list:
            self.redis_node_list = [*self.redis_node_list, *self.__parse_redis_url(url)]

    @staticmethod
    def __parse_redis_url(url: str) -> list:
        arg_list = url.split(":")
        host_name = arg_list[0]
        host_port_range = [int(i) for i in arg_list[1].split("-")]
        if len(host_port_range) == 2:
            host_port_list = range(host_port_range[0], host_port_range[1])
        else:
            host_port_list = host_port_range
        host_url_list = [{"host": host_name, "port": port} for port in host_port_list]
        return host_url_list

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
