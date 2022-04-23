from threading import Thread

from utils.config import get_url_list
from utils.logging import logging

from ..config import async_worker_num, thread_worker_num
from .api_service import run, run_event


def get_work_url_list(worker_url_template):
    url_list = get_url_list(worker_url_template,
                            thread_worker_num * async_worker_num)
    return [
        url_list[x:x + async_worker_num]
        for x in range(0, len(url_list), async_worker_num)
    ]


def _main(discovery_url, worker_url):
    worker_url_list = get_work_url_list(worker_url)
    t_list = run(discovery_url, worker_url_list)
    join(t_list)


def join(t_list: list[Thread]):
    while t_list:
        try:
            _join(t_list)
        except KeyboardInterrupt:
            logging.warning("main stop")
            run_event.set()


def _join(t_list: list[Thread]):
    for t in t_list:
        if t.is_alive():
            t.join()
        else:
            t_list.remove(t)
            logging.warning(f"stop thread: {t}")


def main(discovery_url, worker_url):
    try:
        _main(discovery_url, worker_url)
    except Exception as e:
        logging.error(e)
    logging.warning("the end")
