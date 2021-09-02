from werkzeug.serving import WSGIRequestHandler

from hello.web_api.app import app


def run_api():
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run('0.0.0.0', 5255)
