from hashlib import md5
from threading import Thread
from time import time, sleep

from app.server.manager.data.constant import logging
from app.server.config import server_config


class FunctionRegister:
    thread = None
    timeout = server_config.network_timeout
    function_dict = dict()

    def add_function(self, _key, core):
        key = md5(_key.encode('UTF-8')).digest()
        if key not in self.function_dict:
            self.function_dict[key] = (core, time())
        self._check_dict()

    def call_function(self, _key, *args):
        key = md5(_key.encode('UTF-8')).digest()
        try:
            self.function_dict.pop(key)[0](*args)
        except KeyError:
            logging.info("function_register: non function")
        except Exception as e:
            logging.exception(e)

    def _check_dict(self):
        if not self.thread:
            self.thread = Thread(target=self.__check_dict)
            self.thread.start()

    def __check_dict(self):
        while self.function_dict:
            for k, (core, start_time) in self.function_dict.copy().items():
                if time() - start_time >= self.timeout:
                    core()
                    self.function_dict.pop(k)
            sleep(1)
        self.thread = None


function_register = FunctionRegister()
