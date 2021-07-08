from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from threading import Thread

from .getter_request import WebGetterRequest
from .getter_utils import get_release


class WebGetterManager:
    __parent_conn: Connection
    __child_conn: Connection
    process: Process

    def start(self) -> Process:
        self.__parent_conn, self.__child_conn = Pipe()
        self.process = Process(target=self.__run_getter, args=(self.__child_conn,))
        self.process.start()
        return self.process

    def stop(self):
        self.__parent_conn.send(EOFError)
        self.__parent_conn.close()
        self.process.kill()

    def join(self, timeout=None):
        self.process.join(timeout)

    def send_request(self, request: WebGetterRequest):
        self.__parent_conn.send(request)

    def __run_getter(self, request_conn):
        while True:
            request_item = request_conn.recv()
            if request_item is EOFError:
                break
            thread = Thread(target=self.__do_getter, args=(request_item,))
            thread.start()

    @staticmethod
    def __do_getter(request_item: WebGetterRequest):
        queue = request_item.queue
        iter_core = get_release(request_item.hub_uuid, request_item.app_id_list, request_item.auth,
                                request_item.use_cache, request_item.cache_data, stop_core=lambda: queue.close())
        for app_id, release_list in iter_core:
            queue.add_value((app_id, release_list))


web_getter_manager = WebGetterManager()
