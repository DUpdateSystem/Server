import configparser
import logging

from colorlog import ColoredFormatter

LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"


class ServerConfig:
    def __init__(self):
        self.host = "localhost"
        self.port = 5000
        self.max_workers = 16
        self.debug_mode = True
        self.auto_refresh_time = 6
        self.redis_server_address = "localhost"
        self.redis_server_port = 6379
        self.redis_server_password = ""
        self.log = logging.getLogger('base_logger')
        self.init_logging()

    def init_config_file(self, file_path: str):
        config = configparser.ConfigParser()
        config.read(file_path)
        base_config = config['base']
        self.host = base_config['Host']
        self.port = int(base_config['Port'])
        self.max_workers = int(base_config['MaxWorkers'])
        self.debug_mode = bool(base_config['DebugMode'])
        data_config = config['data']
        self.auto_refresh_time = int(data_config['AutoRefreshTime'])
        web_api_config = config['web_api']
        self.redis_server_address = web_api_config['RedisServerAddress']
        self.redis_server_port = int(web_api_config['RedisServerPort'])
        self.redis_server_password = web_api_config['RedisServerPassword']

    def init_logging(self):
        logging.root.setLevel(LOG_LEVEL)
        formatter = ColoredFormatter(LOG_FORMAT)
        stream = logging.StreamHandler()
        stream.setLevel(LOG_LEVEL)
        stream.setFormatter(formatter)
        self.log.setLevel(LOG_LEVEL)
        self.log.addHandler(stream)


server_config = ServerConfig()
server_config.init_config_file("../config.ini")
logging = server_config.log
