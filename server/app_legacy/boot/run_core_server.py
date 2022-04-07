from multiprocessing import Process

from getter import request_polling


def run_core() -> Process:
    request_polling.start()
