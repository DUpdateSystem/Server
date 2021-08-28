import asyncio
from threading import Thread

from aiohttp import web

from app.cluster.socketio_api.server import app
from app.server.config import server_config
from app.server.utils.utils import set_new_asyncio_loop

loop = set_new_asyncio_loop()
running_lock = asyncio.Lock(loop=loop)


async def _run_site():
    runner = web.AppRunner(app)
    await runner.setup()
    host = server_config.host
    port = server_config.cluster_port
    site = web.TCPSite(runner, host, port)
    await site.start()
    await running_lock.acquire()
    await running_lock.acquire()
    await site.stop()


def run_server():
    loop.run_until_complete(_run_site())


def stop_server():
    loop.run_until_complete(running_lock.release())


def run_cluster_api():
    t = Thread(target=run_server)
    t.start()
