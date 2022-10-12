from inc.inc_functions import percent, add_percent, weighted_average
from inc.inc_system import to2, to8, to6, sleep
# from playground_session import Session
from statistics import mean
import numpy as np
from inc.inc_system import *


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
        self.grid_level_lines = list()
        self.frame = indicators.data.frame
        self.tradebook = [i for i in self.data.tradebook if i['date'] > self.data.from_timestamp]

        self.points = {frame: {'open': {}, 'close': {}} for frame in self.params['time_frames']}
        self.points_cache = {i: {'long': [], 'short': []} for i in ['open', 'close']}

        self.grid_from = 45000
        self.grid_to = 48000
        self.grid_enter_rate = self.data.tradebook[0]['rate']
        self.grid_step_percent = 0.1

        self.level = self.grid_enter_rate
        self.grid_step_value = self.grid_enter_rate / 100 * self.grid_step_percent
        self.grid_segments = int((self.grid_to - self.grid_from) / self.grid_step_value + 1)
        self.grid_levels = self.gen_grid_levels()
        # print(self.grid_orders)

        self.positions = []
        self.grid_trades = []
        self.grid_orders = self.place_orders(self.grid_enter_rate)

        self.total_lots = []

        self.max_position_count = set()
        self.run()
        self.grid_summary()

    def run(self):
        print('total trades in work area', len(self.tradebook))
        for trade in self.tradebook:

            a, b = min(trade['rate'], self.level), max(trade['rate'], self.level)
            crossed_levels = [x for x in self.grid_levels if a <= x <= b]
            # print(crossed_levels)

            if crossed_levels:
                date = utc_timestamp_to_date(find_candle_start_time(trade['date'], self.params['time_frames'][self.frame]))
                cross_level = min(crossed_levels) if trade['rate'] > self.level else max(crossed_levels)
                #   выбираем ближайший уровень к цене

                if trade['type'] == 'buy' and self.grid_orders[cross_level]['type'] == 'short':
                    self.add_job_point('up', date, cross_level, 6, 'red')
                    self.add_position(cross_level, self.grid_orders[cross_level], date)
                    self.place_orders(cross_level)
                    self.analyze_trades()

                if trade['type'] == 'sell' and self.grid_orders[cross_level]['type'] == 'long':
                    self.add_job_point('up', date, cross_level, 5, 'green')
                    self.add_position(cross_level, self.grid_orders[cross_level], date)
                    self.place_orders(cross_level)
                    self.analyze_trades()

            self.level = trade['rate']

    def add_position(self, rate, order, date):
        fee = order['lot'] / 100 * self.params['fee_maker']
        self.positions.append(dict(rate=rate, lot=order['lot'], type=order['type'], date=date, fee=fee))

    def analyze_trades(self):
        if len(self.positions) > 1:
            if self.positions[-1]['type'] != self.positions[-2]['type']:
                self.total_lots.append(sum([i['lots'] for i in self.positions]))
                print(f'total lots: {self.total_lots}')

                average_rate = mean([i['rate'] for i in self.positions])
                fee = self.params['fee_maker']
                profit = sum([abs(percent(i['rate'], rate)) - fee for i in self.positions]) - self.params['fee_maker']
                # profit = abs(percent(average_rate, rate, 3)) - self.params['fee_maker'] * 2
                print(to2(profit))
                self.grid_trades.append(dict(profit=profit, date=self.positions[-2]['date']))
                self.add_job_line(
                    self.positions[-2]['date'],
                    self.positions[-1]['date'],
                    self.positions[-2]['rate'],
                    self.positions[-1]['rate'],
                    profit,
                    'green' if self.positions[-2]['rate'] > self.positions[-1]['rate'] else 'red',
                    size=2)
                self.positions = self.positions[:-2]

    def place_orders(self, rate):
        if self.positions:
            pass
        else:
            levels_above = [i for i in self.grid_levels if i > rate][:3]
            levels_below = [i for i in self.grid_levels if i < rate][-3:]
            grid_orders = {}
            for i, rate in enumerate(levels_below, start=1):
                grid_orders[levels_below[-i]] = {'type': 'long', 'lot': 3 ** (i - 1)}
            for i, rate in enumerate(levels_above, start=1):
                grid_orders[rate] = {'type': 'short', 'lot': 3 ** (i - 1)}
            return grid_orders

    def gen_grid_levels(self):
        levels = []
        for i in range(self.grid_segments):
            level = self.grid_from + self.grid_step_value * i
            levels.append(level)
            self.add_grid_level_line(level)
        return levels

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

    def add_grid_level_line(self, y, color='white', size=0.3):
        self.grid_level_lines.append({
            'y': y,
            'color': color,
            'size': size,
        })

    def grid_summary(self):
        trades_frofit = sum([i['profit'] for i in self.grid_trades])
        print(f'total trades: {len(self.grid_trades)} trades profit: {to2(trades_frofit)} %')
        print(self.positions)
        unclosed_position = sum([percent(i['rate'], self.data.tradebook[-1]['rate']) for i in self.positions])
        print(f'PNL: {to2(unclosed_position)} %')
