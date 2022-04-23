from os import environ

host = '0.0.0.0'
port = 5255


def init_env():
    from discovery.worker_pool.caller import add_pool
    for url in environ['discovery_url'].split(' '):
        add_pool(url)
    if 'database_url' in environ:
        import database.config as db_config
        db_config.db_url = environ['database_url']


init_env()

from hello.web_api.app import app


def run_api():
    app.run(host, port)
