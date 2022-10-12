from multiprocessing import Pipe, Process, Value, current_process, Lock, Array, RawArray
from time import sleep
from ctypes import Structure, c_double, c_wchar_p, c_char_p, c_wchar, c_int


class MarketBalance(Structure):
    _fields_ = [('pair', c_int), ('amount', c_double)]


lst = [1, 2, 3]


class A:
    def __init__(self):
        self.a = 1

    def plus(self, _b):
        self.a += _b
        print('out of pool', self.a)


def job(x, l):
    print(current_process())
    while True:
        print('@1')
        # print(x)
        # msg = _pipe_b.recv()
        # l.acquire()
        # print(current_process(), '->', x[0])
        print(current_process(), '->', [(a.pair, a.amount) for a in x])
        # l.release()
        sleep(0.5)
        # _pipe_a.send('ok')
        # if msg:
        #     if msg == 'exit':
        #         print('process done')
        #         break


def do_multiprocessing(x, l):
    print(f'\r\nCalculating in {processors} threads ...')
    _processes = []
    for i in range(processors):
        process = Process(target=job, args=(x, l))
        process.start()
        _processes.append(process)
    return _processes


if __name__ == '__main__':
    processors = 1
    x = Array(MarketBalance, [(124, 600.25234), (534, 0.00056756), (247, 9.5)], lock=False)
    # a = A()
    # pipe_a, pipe_b = Pipe()
    # x = Value('f', 0, lock=False)
    l = Lock()

    do_multiprocessing(x, l)

    b = 0.2345436
    while True:
        sleep(0.4)
        # x.value += b
        # print(f'--- {x.value}')
        # b += 1
        if b > 10:
            break

    # msg1 = pipe_b.recv()
    # print('--- received in main process', msg1)
