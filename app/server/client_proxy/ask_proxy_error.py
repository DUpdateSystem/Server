from .http_request_item import HttpRequestItem


class NeedClientProxy(Exception):
    def __init__(self, http_request_item: HttpRequestItem):
        self.http_request_item: HttpRequestItem = http_request_item
