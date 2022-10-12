from config import *
from secrets import token_hex
from inc.inc_system import to2, sleep, time, join_args


class ApiQueue:
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.queue = []
        self.queue_lock = False
        self.request_timestamp = time() - 10

    @staticmethod
    def checkin(func):
        def func_wrap(cls, *args, **kwargs):
            token = cls.deco.add_query_to_queue()
            t1 = time()
            _args = join_args(args)
            if cls.deco.check_my_turn_in_queue(token):
                cls.deco.request_timestamp = time()
                res = func(cls, *args, **kwargs)
                t2 = time()
                cls.deco.log.requests(f'{to2(t2 - t1)}с {func.__name__} {_args}')
                return res
            else:
                cls.deco.log.requests(f'{func.__name__} queue error -> {_args} {token}')
            cls.deco.check_queue_health()
        return func_wrap

    def add_query_to_queue(self, priority=0):
        while True:
            if not self.queue_lock:
                self.queue_lock = True
                token = {'hex': token_hex(10), 'time': time()}
                self.queue.insert(0, token) if priority else self.queue.append(token)
                self.queue_lock = False
                return token

    def remove_order_from_queue(self, token):
        while True:
            if not self.queue_lock:
                self.queue_lock = True
                self.queue.remove(token)
                self.queue_lock = False
                break

    def check_my_turn_in_queue(self, token):
        while True:
            if token['hex'] == self.queue[0]['hex']:
                delay = time() - self.request_timestamp
                if delay < conf_request_delay:
                    sleep(conf_request_delay - delay)
                self.remove_order_from_queue(token)
                return True

    def check_queue_health(self):
        if len(self.queue) > 100:
            pass
            self.log.requests('check_queue_health -> over 100 requests in queue')
