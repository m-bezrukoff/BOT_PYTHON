from config import stock
from threading import Thread, currentThread
from classes.cls_dataclasses import ReceiveApiMsg, SendMsg

if stock == 'poloniex':
    from stocks.poloniex.cls_api_http import ApiPoloniex


class Api(ApiPoloniex):
    def __init__(self, glob, log, lock, pipe_pair, pipe_api, pipe_main):
        super().__init__(glob, log)
        self.glob = glob
        self.log = log
        self.lock = lock
        self.pipe_pair = pipe_pair
        self.pipe_api = pipe_api
        self.pipe_main = pipe_main

        self.api_http_threads_count = 4
        self.api_http_threads = [Thread(target=self.run, name=f'api_http_thread_{i}') for i in range(self.api_http_threads_count)]
        self.start_api_http_threads()

    def start_api_http_threads(self):
        for thread in self.api_http_threads:
            # thread.daemon = True
            thread.start()

    def run(self):
        print(f'API thread listening for requests {currentThread().name}')
        while True:
            msg = ReceiveApiMsg(self.pipe_api)

            if msg.action == 'exit':
                print(f'closing {currentThread().name}')
                SendMsg(pipe=self.pipe_api, action='exit')
                break

            else:
                result = getattr(self, msg.action)()
                pipe_obj = getattr(self, msg.reply)
                pipe = pipe_obj[msg.pair] if type(pipe_obj) == dict else pipe_obj
                SendMsg(pipe=pipe, action=msg.action, data=result)
