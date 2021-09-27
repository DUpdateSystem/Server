import logging

import zmq

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

    # Initialize poll set
    poller = zmq.Poller()
    poller.register(frontend, zmq.POLLIN)
    poller.register(backend, zmq.POLLIN)

    # Switch messages between sockets
    while True:
        socks = dict(poller.poll())

        if socks.get(frontend) == zmq.POLLIN:
            message = frontend.recv_multipart()
            backend.send_multipart(message)

        if socks.get(backend) == zmq.POLLIN:
            message = backend.recv_multipart()
            frontend.send_muwltipart(message)

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
