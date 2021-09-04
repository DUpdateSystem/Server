from asyncio import Queue
from multiprocessing import Manager
from queue import SimpleQueue


class BaseQueue:

    def __init__(self, queue):
        self.__queue = queue

    def close(self):
        self.__queue.put(EOFError)

    def put(self, value):
        self.__queue.put(value)

    def get(self):
        return self.__queue.get()

    def __next__(self):
        v = self.get()
        if v is EOFError:
            raise StopIteration
        else:
            return v

    def __iter__(self):
        return self


m = Manager()


class ProcessQueue(BaseQueue):

    def __init__(self):
        super().__init__(m.Queue())


class ThreadQueue(BaseQueue):

    def __init__(self):
        super().__init__(SimpleQueue())


class LightQueue:
    def __init__(self, maxsize=0, loop=None):
        self.__queue = Queue(maxsize, loop=loop)

    async def close(self):
        await self.put(EOFError)

    async def put(self, value):
        await self.__queue.put(value)

    async def get(self):
        return await self.__queue.get()

    async def __anext__(self):
        v = await self.get()
        if v is EOFError:
            raise StopAsyncIteration
        else:
            return v

    def __aiter__(self):
        return self
