from multiprocessing import Process

from getter.request_processor.polling import request_polling


def run_core() -> Process:
    request_polling.start()
