from inc.inc_functions import percent, add_percent
from inc.inc_system import *


class Summary:
    def __init__(self, worker):
        # self.data = worker.data
        self.params = worker.params
        # self.frame = worker.frame
        # self.frame_size = worker.jobframe_size
        self.summary = worker.job.summary

        self.profit_trades = 0
        self.loss_trades = 0
        self.win_rate = 0
        self.total_percent = 0
        self.total_trades = len(self.summary)

        self.run()

    def run(self):
        for session in self.summary:
            if session['result'] > 0:
                self.profit_trades += 1
            else:
                self.loss_trades += 1

            self.total_percent += session['result']

        self.win_rate = round((self.profit_trades / self.total_trades) * 100, 0) if self.total_trades else 0

        s = '\033[32m' if self.total_percent > 0 else '\033[31m'
        e = '\033[0m'

        print('='*80)
        print(f'{s}total trades: {self.total_trades}    win rate: {self.win_rate} %   profit: {to2(self.total_percent)} %{e}')
        print('='*80)
