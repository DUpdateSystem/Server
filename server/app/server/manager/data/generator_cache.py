from queue import SimpleQueue


class GeneratorCache:

    def __init__(self):
        self.__queue = SimpleQueue()

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
