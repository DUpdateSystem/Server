from multiprocessing import Manager
from queue import SimpleQueue


class BaseGeneratorCache:

    def __init__(self, queue):
        self.__queue = queue

    def close(self):
        self.__queue.put(EOFError)

    def add_value(self, value):
        self.__queue.put(value)

    def __next__(self):
        v = self.__queue.get()
        if v is EOFError:
            raise StopIteration
        else:
            return v

    def __iter__(self):
        return self


m = Manager()


class ProcessGeneratorCache(BaseGeneratorCache):

    def __init__(self):
        super().__init__(m.Queue())


class GeneratorCache(BaseGeneratorCache):

    def __init__(self):
        super().__init__(SimpleQueue())
