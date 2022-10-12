from multiprocessing import Queue, Process
import time

list = [1, 2, 3]


class A:
    def __init__(self):
        self.a = 1

    def plus(self, b):
        self.a += b
        print('out of pool', self.a)


def job(_queue: Queue, _a: A):
    for i in range(1000):
        # print(_a)
        _a.a += 1
    _queue.put(_a)
    # print('out of process', _a.a)


def do_multiprocessing(_queue: Queue, _a: A) -> list:
    print(f'\r\nCalculating in {processors} threads ...')
    _processes = []
    for i in range(processors):
        process = Process(target=job, args=(_queue, _a))
        process.start()
        _processes.append(process)
    return _processes


if __name__ == '__main__':
    processors = 1
    a = A()
    tasks_queue = Queue()    # очередь заданий
    results_queue = Queue()  # очередь результаттов

    do_multiprocessing(results_queue, a)
    while results_queue.empty():
        pass

    a = results_queue.get()
    print('out of main', a.a)
