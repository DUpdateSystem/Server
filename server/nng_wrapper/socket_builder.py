from pynng import Rep0, Req0

from .constant import recv_timeout_ms


def req0(address):
    sock = Req0(recv_timeout=recv_timeout_ms)
    sock.dial(address, block=True)
    return sock


def rep0(address):
    sock = Rep0(recv_timeout=recv_timeout_ms)
    sock.listen(address)
    return sock
