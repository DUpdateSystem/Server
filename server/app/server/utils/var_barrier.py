from multiprocessing import Event, Value


class VarBarrier:
    thread_num = Value('i', 0)
    wait_thread_num = Value('i', 0)
    event = Event()

    def register(self):
        print("re")
        with self.thread_num.get_lock():
            self.thread_num.value += 1

    def unregister(self):
        print("unre")
        with self.thread_num.get_lock():
            self.thread_num.value -= 1

    def only_wait(self):
        self.event.wait()

    def wait(self):
        wait = False
        with self.wait_thread_num.get_lock():
            if self.wait_thread_num.value >= self.thread_num.value - 1:
                self.reset()
            else:
                self.wait_thread_num.value += 1
                wait = True
        if wait:
            self.event.wait()

    def reset(self):
        self.event.set()
        self.event.clear()
        self.wait_thread_num.value = 0
