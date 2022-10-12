from sys import stdout
from time import time
import datetime


def to2(_):
    return format(_, '.02f')


class ProgressBar:
    def __init__(self, total, model='reversed'):
        self.total = total
        self.remain = 0
        self.time = 0
        self.last_time = 0
        self.time_passed = 0
        self.time_begin = time()
        self.last_val = 0
        self.len = 50
        self.status = ''
        self.model = model
        self.ratio = 0

        self.delta = []
        self.speed = 0
        self.eta = 0

        self.block = 0
        self.indicator = ''

    def update(self, progress):
        progress = float(progress)

        if self.model == 'reversed':
            self.time = time()
            self.remain = progress
            self.ratio = (self.total - self.remain) / self.total if self.total else 0
            if self.last_time:
                self.delta.append([self.time - self.last_time, abs(progress - self.last_val)])
                self.delta = self.delta[-30:]

                t = 0
                v = 0
                c = len(self.delta)
                for _ in self.delta:
                    t += _[0]
                    v += _[1]

                    self.speed = v / t
                    if self.speed:
                        self.eta = int(self.remain / self.speed)
                        if self.eta > 60:
                            self.eta = str(datetime.timedelta(seconds=self.eta))

            self.last_time = self.time
            self.last_val = progress

            self.block = int(round(self.len * self.ratio))
            self.indicator = '#' * self.block + '-' * (self.len - self.block)
            self.time_passed = int(self.time - self.time_begin)
            if self.time_passed > 60:
                self.time_passed = str(datetime.timedelta(seconds=self.time_passed))

        text = '\rProgress: [{}] \033[31m{}%\033[0m rate: {} eta: \033[32m{}\033[0m passed: {}\r'\
            .format(self.indicator, to2(self.ratio * 100), to2(self.speed), self.eta, self.time_passed)
        stdout.write(text)
        stdout.flush()

        # if self.ratio >= 1:
        #     stdout.write('\r\n')
