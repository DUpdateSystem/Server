import zmq

from utils.logging import logging
from .url import front_url, end_url


def main():
    """ main method """

    context = zmq.Context()

    # Socket facing clients
    frontend = context.socket(zmq.ROUTER)
    frontend.bind(front_url)

    # Socket facing services
    backend = context.socket(zmq.DEALER)
    backend.bind(end_url)

    zmq.proxy(frontend, backend)

    # We never get here...
    frontend.close()
    backend.close()
    context.term()


def run():
    try:
        logging.info(f"proxy start, front: {front_url}, end: {end_url}")
        main()
    except KeyboardInterrupt:
        logging.info("proxy stop")
