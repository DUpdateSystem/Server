from threading import Thread
from config import worker_url, discovery_url, thread_worker_num, async_worker_num
from utils.config import get_url_list
from utils.logging import logging
from .api_service import run, run_event


def get_work_url_list(worker_url_template):
    thread_worker_url_list = [
        thread_worker_url for thread_worker_url in get_url_list(
            worker_url_template, thread_worker_num)
    ]
    return [[
        async_worker_url for async_worker_url in get_url_list(
            thread_worker_url, async_worker_num)
    ] for thread_worker_url in thread_worker_url_list]


def _main():
    worker_url_list = get_work_url_list(worker_url)
    t_list = run(worker_url_list)
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


def main():
    try:
        _main()
    except Exception as e:
        logging.error(e)
    logging.warning("the end")
