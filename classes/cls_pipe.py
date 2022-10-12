from multiprocessing import Pipe


class MyPipe:
    def __init__(self):
        self.a, self.b = Pipe()
