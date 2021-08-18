from app.server.config import server_config
from app.web_api.app import app


def run_api():
    host = server_config.host
    port = server_config.port
    app.run(host, port, server_config.debug_mode)
