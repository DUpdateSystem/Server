from pynng import Req0, Rep0
from .constant import recv_timeout


def req0(address):
    sock = Req0(recv_timeout=recv_timeout)
    sock.dial(address, block=True)
    return sock


def rep0(address):
    sock = Rep0(recv_timeout=recv_timeout)
    sock.listen(address)
    return sock
