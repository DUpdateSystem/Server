import configparser


class ServerConfig:
    def __init__(self):
        self.host = "localhost"
        self.port = 5000
        self.debug_mode = True
        self.auto_refresh_time = 6
        self.redis_server_address = "localhost"
        self.redis_server_port = 6379

    def init_config(self, file_path: str):
        config = configparser.ConfigParser()
        config.read(file_path)
        base_config = config['base']
        self.host = base_config['Host']
        self.port = int(base_config['Port'])
        self.debug_mode = bool(base_config['DebugMode'])
        data_config = config['data']
        self.auto_refresh_time = int(data_config['AutoRefreshTime'])
        web_api_config = config['web_api']
        self.redis_server_address = web_api_config['RedisServerAddress']
        self.redis_server_port = int(web_api_config['RedisServerPort'])


server_config = ServerConfig()
server_config.init_config("../config.ini")
