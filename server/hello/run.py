from hello.web_api.app import app

host = '0.0.0.0'
port = 5255


def run_api():
    app.run(host, port)
