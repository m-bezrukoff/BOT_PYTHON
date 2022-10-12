# from ai._keras_train import keras_train_complex
# from ai.ai_keras_simulator import render_test_data
from simulator_v2.playground_indicators import Indicators
from simulator_v2.playground_plotly import Graphics
from simulator.enter_points import *
from inc.inc_system import *


class Data:
    def __init__(self, pair, params, frame, start, length):
        self.pair = pair
        self.frame = frame
        self.start = start
        self.length = length
        self.params = params
        self.charts = self.get_charts(start, length)

        print(self.charts[0]['utc_date'], '-', self.charts[-1]['utc_date'])

    def get_charts(self, start=None, length=None):
        _res = load_zipped_pickle('../simulator/save/' + self.pair + '_charts.dat')
        return _res[self.frame][start:start + length] if start and length else _res[self.frame]

    # def cut_by_time(_charts, start, length):
    #     i = 0
    #     for i in range(len(_charts)):
    #         if charts[i]['timestamp'] == start:
    #             break
    #     return _charts[i:i+length]


if __name__ == '__main__':
    # charts = get_charts('BTC_ETH', start=0, length=430000)
    # charts = get_charts('BTC_ETH', start=420000, length=8640)
    # charts = get_charts('USDT_BTC', start=550000, length=8640)
    # charts = get_charts('USDT_TRX', frame='5m', start=100000, length=8640)
    # charts = get_charts('USDT_BTC', start=550000, length=8640)
    # charts = cut_by_time(get_charts('USDT_BTC'), 1525974900, 8640)
    # print('start:', charts[0]['utc_date'])

    params = {
        'macd_f': 12,
        'macd_s': 26,
        'macd_sig': 9,

        'ema_f': 180,
        'ema_m': 180,
        'ema_s': 108,

        'c_size': 300,
        'stop_loss': -1.6,
        'in_lim_down': -135,
        'in_lim_up': -125,
        'out_lim_up': 65,
        'out_lim_down': 65,
    }
    data = Data('USDT_TRX', params, frame='30m', start=12000, length=288 * 3)
    indicators = Indicators(data, params)
    job = Job(indicators)
    graphics = Graphics(job)
