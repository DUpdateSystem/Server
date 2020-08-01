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
        cache_db_config = config['cache_db']
        self.use_cache_db = bool(strtobool(cache_db_config['UseCacheDB']))
        self.redis_server_address = cache_db_config['RedisServerAddress']
        self.redis_server_port = int(cache_db_config['RedisServerPort'])
        self.redis_server_password = cache_db_config['RedisServerPassword']


server_config = _ServerConfig("./config.ini")
