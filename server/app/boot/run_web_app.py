from werkzeug.serving import WSGIRequestHandler

from app.server.config import server_config
from hello.web_api import app


def run_api():
    host = server_config.host
    port = server_config.port
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host, port)
