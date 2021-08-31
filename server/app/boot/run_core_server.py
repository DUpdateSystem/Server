from multiprocessing import Process

from app.server.request_processor.polling import request_polling


def run_core() -> Process:
    request_polling.start()
