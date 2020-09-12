from asyncio import Event

from app.server.utils import set_new_asyncio_loop, call_def_in_loop_return_result


class GeneratorCache:
    __loop = set_new_asyncio_loop()
    __cache_queue = []
    __next_lock = Event()

    def __init__(self, size):
        self.__length = size

    def add_value(self, value):
        self.__cache_queue.append(value)
        self.__next_lock.set()

    def __next__(self):
        self.__length -= 1
        if self.__length < 0:
            raise StopIteration
        return call_def_in_loop_return_result(self.__get_next_item(), self.__loop)

    def __iter__(self):
        return self

    async def __get_next_item(self):
        await self.__next_lock.wait()
        v = self.__cache_queue.pop(0)
        if not self.__cache_queue:
            self.__next_lock.clear()
        return v
