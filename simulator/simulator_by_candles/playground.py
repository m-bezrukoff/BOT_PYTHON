from playground_data import Data
from playground_summary import Summary
from playground_plotly import Graphics
from playground_indicators import Indicators
from playground_grid import Job
from inc.inc_system import *


class Worker:
    def __init__(self, _params, _data=None, printer=True):
        self.processes_list = []
        self.params = _params
        self.data = _data
        self.printer = printer
        self.trades_total = len(self.data.tradebook)
        self.graphics_data = {}
        if printer:
            self.print_info()
        self.indicators = Indicators(self.data)
        self.job = Job(self.indicators)
        # self.summary = Summary(self)

    def print_info(self):
        print('time_frames', self.params['time_frames'])
        print('from time:', self.data.from_timestamp, ' - ', self.params['from'])
        print('to time:  ', self.data.to_timestamp, ' - ', self.params['to'])
        print('')
        print('first trade time:', self.data.tradebook[0]['date'], utc_timestamp_to_date(self.data.tradebook[0]['date']))
        print('last  trade time:', self.data.tradebook[-1]['date'], utc_timestamp_to_date(self.data.tradebook[-1]['date']))
        print('')
        print('trades total:', self.trades_total)
        print('')
        for frame in self.params['time_frames']:
            print(f'charts frame {frame}: {self.data.charts[frame]["utc_date"][0]} - {self.data.charts[frame]["utc_date"][-1]}')


if __name__ == '__main__':
    params = {
        'pair': 'USDT_BTC',
        'from': '2021-03-01 00:00:00',
        'to': '2021-03-01 12:00:00',

        'time_frames': {'30s': 30},
        # 'time_frames': {'1m': 60},
        # 'time_frames': {'5m': 300},
        # 'time_frames': {'15m': 900},
        # 'time_frames': {'1h': 3600},
        'fee_maker': 0.01,    # %
        'fee_taker': 0.075,     # %

        # 'time_frames': {'1m': 60, '3m': 180, '5m': 300, '10m': 600, '15m': 900, '30m': 1800, '1h': 3600},
        'tools': {
            # 'atr': {
            #     'method': 'ATR',
            #     'period': 14,
            # },
            'ema_50': {
                'method': 'EMA',
                'input_data': 'c',
                'period': 50,
                'color': 'yellow',
                'width': 2
            },
            # 'jma_f': {
            #     'method': 'JMA',
            #     'input_data': 'm',
            #     'period': 5,
            #     'color': 'red',
            #     'width': 2
            # },
            # 'jma_s': {
            #     'method': 'JMA',
            #     'input_data': 'm',
            #     'period': 8,
            #     'color': 'orange',
            #     'width': 2
            # },
            'ema_200': {
                'method': 'EMA',
                'input_data': 'c',
                'period': 200,
                'color': 'white',
                'width': 2
            },
            # 'ema_100': {
            #     'method': 'EMA',
            #     'input_data': 'c',
            #     'period': 100,
            #     'color': 'cyan',
            #     'width': 2
            # },
            # 'ma_speed': {
            #     'method': 'MA_SPEED',
            #     'input_data': 'ema_200',
            #     'color': 'green',
            #     'width': 1
            # },
            # 'ma_channel': {
            #     'method': 'MA_CHANNEL',
            #     'input_data': 'ema_50',
            #     # 'driver_data': 'ma_speed',
            #     'driver_data': 'ma_speed',
            #     'color_up': 'green',
            #     'color_down': 'red',
            #     'width': 0.5
            # },
            # 'ma_candle_relation': {
            #     'method': 'MA_CANDLE_RELATION',
            #     'input_data': 'jma_f',
            #     'color': 'green',
            #     'width': 1
            # },
            # 'macd': {
            #     'method': 'CUSTOM_MACD',
            #     'input_data': 'ema_50',
            #     'color': 'green',
            #     'width': 1
            # },
            # 'bb_b': {
            #     'method': 'BB_B',
            #     'input_data': 'c',
            #     'period': 14,
            #  },
            # 'ao': {
            #     'method': 'AO',
            #  },
            # 'adx': {
            #     'method': 'ADX',
            #     'period': 14,
            #  },

            # 'jma_f': {
            #     'method': 'JMA',
            #     'input_data': 'c',
            #     'period': 5,
            #     'phase': 100,
            #     'power': 1,
            #     'color': 'red',
            #     'width': 1.5
            # },
            # 'jma_s': {
            #     'method': 'JMA',
            #     'input_data': 'c',
            #     'period': 8,
            #     'phase': 100,
            #     'power': 1,
            #     'color': 'violet',
            #     'width': 1.5
            # },
        },
    }

    t1 = time()
    data = Data(params)
    w = Worker(params, data)
    t2 = time()
    print(f'total time spent: {to2(t2 - t1)} sec \r\n {"-" * 40}')
    graphics = Graphics(w)
