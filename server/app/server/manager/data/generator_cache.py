from asyncio import Event

from app.server.utils import set_new_asyncio_loop, call_def_in_loop_return_result


class GeneratorCache:

    def __init__(self):
        self.__loop = set_new_asyncio_loop()
        self.__cache_queue = []
        self.__next_lock = Event()
        self.__closed = False

    def close(self):
        self.__cache_queue.append(None)
        self.__closed = True

    def add_value(self, value):
        self.__cache_queue.append(value)
        self.__next_lock.set()

    def __next__(self):
        v = call_def_in_loop_return_result(self.__get_next_item(), self.__loop)
        if self.__closed and v is None:
            raise StopIteration
        return v

    def __iter__(self):
        return self

    async def __get_next_item(self):
        await self.__next_lock.wait()
        v = self.__cache_queue.pop(0)
        if not self.__cache_queue:
            self.__next_lock.clear()
        return v
