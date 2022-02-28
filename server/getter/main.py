import asyncio

from config import worker_url, discovery_url, thread_worker_num, async_worker_num
from discovery.client_utils import keep_register_service_address
from utils.config import get_url_list
from .api_service import run


def get_work_url_list(worker_url_template):
    thread_worker_url_list = [thread_worker_url for thread_worker_url in
                              get_url_list(worker_url_template, thread_worker_num)]
    return [[
        async_worker_url
        for async_worker_url in get_url_list(thread_worker_url, async_worker_num)
    ] for thread_worker_url in thread_worker_url_list]


def main():
    worker_url_list = get_work_url_list(worker_url)
    run(worker_url_list)
    asyncio.run(keep_register_service_address(discovery_url, worker_url_list))
