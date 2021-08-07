import logging
from threading import Thread

from flask import Flask
from werkzeug.serving import make_server

from app.server.config import server_config
from app.starter.run_grpc_server import restart_grpc
from .status import get_grpc_available, get_redis_availability, __hub_available_key_list


class ServerThread(Thread):

    def __init__(self, host: str, port: int):
        Thread.__init__(self)
        self.srv = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


app = Flask(__name__)
app.logger.disabled = True
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/status')
def check_status():
    if not get_redis_availability():
        return "no redis connect", 503
    elif len(__hub_available_key_list) == 0:
        return "no hub available", 503
    elif isinstance(get_grpc_available(), Exception):
        restart_grpc()
        return f"grpc shutdown", 503
    else:
        return '', 204


checker_thread = ServerThread(server_config.host, server_config.checker_port)
