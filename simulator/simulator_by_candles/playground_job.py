from inc.inc_functions import percent, add_percent, weighted_average
from inc.inc_system import to2, to8, to6, sleep
from playground_session import Session
from statistics import mean
import numpy as np


class Job:
    def __init__(self, indicators):
        self.margin = indicators.data.margin_candles
        self.params = indicators.params
        self.data = indicators.data
        self.charts = indicators.data.charts
        self.indicators = indicators
        self.arr = indicators.arr
        self.job_points = dict()
        self.job_lines = list()
        self.frame = indicators.data.frame

        self.points = {frame: {'open': {}, 'close': {}} for frame in self.params['time_frames']}
        self.points_cache = {i: {'long': [], 'short': []} for i in ['open', 'close']}
        self.rate = 0
        # self.margin = {frame: int((self.data.from_timestamp - self.data.to_timestamp) // self.params['time_frames'][frame]) for frame in self.params['time_frames']}
        self.session = Session()
        self.summary = []

        self.run()

    def run(self):
        total_candles = len(self.charts[self.frame]['o'])
        print('-'*80)
        print('total candel', total_candles)

        for limiter in range(self.margin + 1, total_candles + 1):
            charts = {self.frame: {key: val[limiter - self.margin:limiter] for key, val in self.charts[self.frame].items()}}
            arr = {self.frame: {key: val[limiter - self.margin:limiter] for key, val in self.indicators.arr[self.frame].items()}}
            o = charts[self.frame]['o']
            h = charts[self.frame]['h']
            l = charts[self.frame]['l']
            c = charts[self.frame]['c']
            date = charts[self.frame]['utc_date']

            if not self.session:
                self.strategy(self.frame, charts, arr, o, h, l, c, date)

            if self.session:
                if self.session['direction'] == 'long':
                    if l[-1] < self.session['stop_loss']:
                        self.close_session(self.session['stop_loss'], date[-1], is_profitable=False)
                        return None

                    if h[-1] >= self.session['take_profit']:
                        self.close_session(self.session['take_profit'], date[-1])
                else:
                    if h[-1] > self.session['stop_loss']:
                        self.close_session(self.session['stop_loss'], date[-1], is_profitable=False)
                        return None

                    if l[-1] <= self.session['take_profit']:
                        self.close_session(self.session['take_profit'], date[-1])

    def strategy(self, frame, charts, arr, o, h, l, c, date):

        ema_50 = arr[frame]['ema_50']
        ema_200 = arr[frame]['ema_200']
        jma_f = arr[frame]['jma_f']
        jma_s = arr[frame]['jma_s']
        # bb_b = arr[frame]['bb_b_b']
        # adx = arr[frame]['adx']
        # ao = arr[frame]['ao']
        # ema_f = arr[frame]['ema_f']
        # ma_speed = arr[frame]['ma_speed']
        mcr = arr[frame]['ma_candle_relation']
        ratio = 1.5

        if not self.session:
            pass
        if all((
                # mcr[-2] < -80,
                # ema_50[-3] < ema_50[-2],
                # ema_200[-3] < ema_200[-2],
                # ema_50[-2] > ema_200[-2],
                # jma_f[-3] > jma_f[-2],
                jma_f[-2] > jma_s[-2],
                jma_f[-3] < jma_s[-3]
        )):
            self.add_job_point('up', date[-1], o[-1], 5, 'green')

            # self.add_job_point('up', date[-1], o[-1], 5, 'green')
            # open_rate = o[-1]
            # stop_loss = add_percent(open_rate, -2)
            # take_profit = add_percent(open_rate, 1)
            # self.open_session('long', open_rate, date[-1], take_profit, stop_loss)

    def close_long(self, frame):
        # tail_down = (min(o, c) - l) / ((h - l) / 100) if (h - l) != 0 else 0
        # if tail_up > 45:
        #             self.add_job_point('tail_up', date, 0.9995 * l, 5, 'green')
        # print(date, ma_speed[-2], '%')
        # max_peaks = self.indicators.arr[frame]['points_max_peaks']
        # last_min = min(self.charts[frame]['l'][-4:])
        pass

    def last_peak_to_rate_diff(self, frame):
        h = self.charts[frame]['h']
        for i in range(-1, -len(h), -1):
            if (h[i-4] <= h[i-3] >= h[i-2]) and (h[i-5] <= h[i-3] >= h[i-1]):
                return percent(h[i-2], self.rate)
        return False

    def add_job_point(self, point_type, x, y, symbol, color, size=11):
        if point_type not in self.job_points:
            self.job_points[point_type] = {'x': [], 'y': [], 'symbol': [], 'color': [], 'size': []}

        self.job_points[point_type]['x'].append(x)
        self.job_points[point_type]['y'].append(y)
        self.job_points[point_type]['symbol'].append(symbol)
        self.job_points[point_type]['color'].append(color)
        self.job_points[point_type]['size'].append(size)

    def add_job_line(self, x1, x2, y1, y2, result, color, size=2):
        self.job_lines.append({
            'x1': x1,
            'x2': x2,
            'y1': y1,
            'y2': y2,
            'result': result,
            'color': color,
            'size': size,
        })

    def open_session(self, direction, open_rate, open_date, take_profit, stop_loss):
        if not self.session:
            self.session = {
                'direction': direction,
                'open_rate': open_rate,
                'open_date': open_date,
                'take_profit': take_profit,
                'stop_loss': stop_loss
            }

    def close_session(self, close_rate, close_date, is_profitable=True):
        if self.session:
            fee = self.params['fee_taker'] + self.params['fee_maker'] if is_profitable else 2 * self.params['fee_taker']
            # fee = 0
            result = percent(self.session['open_rate'], close_rate) - fee

            if self.session['direction'] == 'short':
                result = -result

            string = {
                'direction': self.session['direction'],
                'open_rate': self.session['open_rate'],
                'open_date': self.session['open_date'],
                'close_rate': close_rate,
                'close_date': close_date,
                'result': result
            }
            self.summary.append(string)
            color = 'green' if is_profitable else 'red'
            self.add_job_line(string['open_date'], string['close_date'], string['open_rate'], string['close_rate'], result, color, size=4)

            s = '\033[32m' if string["result"] > 0 else '\033[31m'
            e = '\033[0m'
            print(f'{s}{string["open_date"]} {string["close_date"]} {to2(string["result"])} % {e}')

        self.session = {}

