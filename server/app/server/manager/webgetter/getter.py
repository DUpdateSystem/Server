from threading import Thread, RLock
from time import sleep

from .getter_request_list import getter_request_list
from .getter_utils import get_release


class WebGetterManager:
    thread: Thread or None = None
    thread_lock = RLock()

    def start(self) -> Thread:
        if not self.thread:
            self.thread = Thread(target=self.__run_getter)
            self.thread.start()
        return self.thread

    def join(self, timeout=None):
        if self.thread:
            self.thread.join(timeout)

    def send_request(self, hub_uuid: str, auth: dict, app_id: dict, callback, use_cache: bool = True):
        getter_request_list.add_request(hub_uuid, auth, app_id, callback, use_cache)
        self.start()

    def __run_getter(self):
        while not getter_request_list.is_empty():
            sleep(1)
            hub_uuid, auth, use_cache, app_id_list = getter_request_list.pop_request_list()
            thread = Thread(target=self.__do_getter, args=(hub_uuid, auth, use_cache, app_id_list))
            thread.start()
            sleep(2)
        self.thread_lock.acquire()
        self.thread = None
        self.thread_lock.release()

    def __do_getter(self, hub_uuid: str, auth: dict, use_cache: bool, app_id_list: list):
        self.thread_lock.acquire(blocking=False)
        iter_core = get_release(hub_uuid, app_id_list, auth, use_cache)
        for app_id, release_list in iter_core:
            getter_request_list.callback_request(hub_uuid, auth, use_cache, app_id, release_list)
        self.thread_lock.release()


web_getter_manager = WebGetterManager()
