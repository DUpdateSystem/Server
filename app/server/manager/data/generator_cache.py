from multiprocessing import SimpleQueue


class GeneratorCache:
    __queue = SimpleQueue()
    __closed = False

    def close(self):
        self.__closed = True
        self.__queue.put(None)

    def add_value(self, value):
        self.__queue.put(value)

    def __next__(self):
        value = self.__queue.get()
        if value is None and self.__closed:
            raise StopIteration
        return value

    def __iter__(self):
        return self
