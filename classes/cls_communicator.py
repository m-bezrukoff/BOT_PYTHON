from threading import Thread, currentThread


class ProcessCommunicator:
    """
    Создает pipes между процессами пар и основным процессом.
    """
    def __init__(self, lock, pipe_api, pipe_socket, pipe_main, log):
        self.lock = lock
        self.log = log
        self.pipe_api = pipe_api
        self.pipe_socket = pipe_socket
        self.pipe_main = pipe_main.b
        self.communicator_threads_count = 1
        self.communicator_threads = [Thread(target=self.run, name=f'communicator_thread_{i}') for i in range(self.communicator_threads_count)]

    def run(self):
        self.lock.acquire()
        print(f'main thread listening for requests {currentThread().name}')
        self.lock.release()
        while True:
            msg = self.pipe_main.recv()
            print(f'main thread {currentThread().name} -> {msg}')

            _type = msg.get('type')
            _action = msg.get('action')
            _pipe = msg.get('pipe')
            _pair = msg.get('pair')
            _data = msg.get('data')

            if _type == 'post':
                if _action == 'log':
                    self.log.log(_pair, _data)
                    # getattr(self.log, msg['action'])(_pair, _data)

            if _type == 'exit':
                # self.pipe_exit.send(pipe_msg('exit'))
                break
