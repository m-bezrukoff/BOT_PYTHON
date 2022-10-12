from playground_data import Data
from playground_summary import Summary
from playground_plotly import Graphics
from playground_indicators import Indicators
from playground_enter_points import Job
from inc.inc_system import *


class Worker:
    def __init__(self, _params, _data=None, printer=True):
        self.processes_list = []
        self.params = _params
        self.printer = printer
        self.frame = self.params['frame']
        self.frame_size = self.params['time_frames'][self.frame]
        self.data = _data if _data else Data(self.params)
        self.data.params = _params
        self.trades_total = len(self.data.tradebook)
        self.graphics_data = {}
        if printer:
            self.print_info()
        self.indicators = Indicators(self.data)
        self.job = Job(self.indicators)
        self.summary = object
        self.run()

    def print_info(self):
        print('time_frames', self.params['time_frames'])
        print('from time:', self.data.from_timestamp, ' - ', self.params['from'])
        print('to time:  ', self.data.to_timestamp, ' - ', self.params['to'])
        print('')
        print('first trade time:', self.data.tradebook[0]['date'], utc_timestamp_to_date(self.data.tradebook[0]['date']))
        print('last  trade time:', self.data.tradebook[-1]['date'], utc_timestamp_to_date(self.data.tradebook[-1]['date']))
        print('')
        print('first candle time:', self.data.charts[self.frame]['timestamp'][0], utc_timestamp_to_date(self.data.charts[self.frame]['timestamp'][0]))
        print('last  candle time:', self.data.charts[self.frame]['timestamp'][-1], utc_timestamp_to_date(self.data.charts[self.frame]['timestamp'][-1]))
        print('')
        print('trades total:', self.trades_total)

    def run(self):
        t = time()
        t1 = t2 = t3 = t4 = 0
        t11 = t22 = t33 = 0
        for i in self.data.tradebook[self.data.tradebook_limiter:]:
            t1 = time()
            self.data.update_charts(int(i['date']), float(i['rate']), float(i['amount']), i['type'])
            t11 += time() - t1
            t2 = time()
            self.indicators.incremental_indicators_update()
            t22 += time() - t2
            t3 = time()
            self.job.run()
            t33 += time() - t3
        t4 = time()
        self.summary = Summary(self)

        if self.printer:
            print('iterations:', to2(time() - t))
            print('    charts:', to2(t11))
            print('   indicators:', to2(t22))
            print('        indicators full:', to2(self.indicators.time_1))
            print('        indicators incremental:', to2(self.indicators.time_2))
            print('    job time:', to2(t33))
            print('    summary time:', to2(time() - t4))
            print('--------------------------------------------\r\n')


if __name__ == '__main__':

    params = {
        'pair': 'USDT_TRX',
        'frame': '1m',
        'time_frames': {'1m': 60},
        # 'time_frames': {'1m': 60, '3m': 180, '5m': 300, '10m': 600, '15m': 900, '30m': 1800},

        # 'from': '2021-03-20 00:00:00',        # растущий тренд
        # 'to':   '2021-03-20 06:00:00',

        'from': '2021-03-01 00:00:00',
        'to':   '2021-03-15 00:00:00',


        'ema_f': 8,
        'ema_f_phase': -50,
        'ema_f_power': 1,

        'ema_m': 14,
        'ema_m_phase': -50,
        'ema_m_power': 1,
    }

    t10 = time()
    w = Worker(params)
    print('total time spent:', to2(time() - t10), 'sec')
    print('--------------------------------------------\r\n')
    graphics = Graphics(w)
