from inc.inc_system import find_candle_start_time, sleep, time, utc_timestamp_to_date
from inc.inc_functions import weighted_average, percent
from simulator.sim.sim_config import *
from inc.inc_system import join_args, local_timestamp_to_date
from classes.cls_log import Log
from stocks.poloniex.cls_api_poloniex_http import Api
from classes.cls_charts import Charts
from classes.cls_trades_public import TradesPublic
from classes.cls_trades_private import PrivateTrades
from classes.cls_indicators import Indicators
# import pandas as pd


class SimLog(Log):
    def __init__(self):
        super().__init__()

    def log(self, pair, *args):
        print(join_args(args))


class SimApi(Api):
    def __init__(self, glob, log):
        super().__init__(glob, log)

    def log(self, pair, *args):
        print(join_args(args))


class SimPublicTrades(TradesPublic):
    def __init__(self, pair, api, log):
        super().__init__(pair, api)
        print(len(self.data), 'trades loaded')


class SimPrivateTrades(PrivateTrades):
    def __init__(self, pair, api, log):
        super().__init__(pair, api, log)

    def load_private_trades(self):
        return []


class SimIndicators(Indicators):
    def __init__(self, pair, pairs, charts, public_trades, private_trades, socket_server):
        super().__init__(pair, pairs, charts, public_trades, private_trades, socket_server)

    def sim_export_graphics_data(self, pair):
        if time() - self.time_last_export > conf_graph_rotation_delay:
            limit = 30
            frame = self.glob.display_timeframe
            msg = {
                'frames': [i for i in conf_time_frames],
                'time': local_timestamp_to_date(),
                'pair': pair,
                'bid': self.pairs.bid_rate,
                'ask': self.pairs.ask_rate,
                'rate': self.pairs.rate,
                'date': self.list_date[frame][limit:],
                'open': self.arr_open[frame][limit:].tolist(),
                'close': self.arr_close[frame][limit:].tolist(),
                'high': self.arr_high[frame][limit:].tolist(),
                'low': self.arr_low[frame][limit:].tolist(),
                'volume': self.arr_volume[frame][limit:].tolist(),
                'amplitude': ['amplitude {}%'.format(i['amplitude']) for i in self.charts.data[frame][-limit:]],

                'macd_m': self.macd_m[frame][limit:].tolist(),
                'macd_h': self.macd_h[frame][limit:].tolist(),
                'macd_c': self.macd_c[frame][limit:],
                'macd_s': self.macd_s[frame][limit:].tolist(),

                'ema_f': self.ema_f[frame][limit:].tolist(),
                'ema_s': self.ema_s[frame][limit:].tolist(),
                'clusters': self.clusters[frame],
                'trade_points': self.update_trade_points(frame)
            }
            self.socket_server.send(msg)


class SimCharts(Charts):
    def __init__(self, pair, api, glob, log):
        super().__init__(pair, api)
        print('charts', len(self.data))

    def update_by_sim(self, date, rate, amount, typ):
        if self.data:
            for frame in conf_time_frames:   # перебираем активные таймфреймы
                now = find_candle_start_time(date, frame)
                new = True
                if self.data[frame]:
                    if self.data[frame][-1]['timestamp'] == now:    # обновление свечи, если она уже есть
                        new = False
                        if not self.cache[frame]['o']:
                            self.cache[frame]['o'] = self.cache[frame]['c'] = self.cache[frame]['h'] = self.cache[frame]['l'] = rate
                        if rate > self.cache[frame]['h']:
                            self.cache[frame]['h'] = rate
                        if rate < self.cache[frame]['l']:
                            self.cache[frame]['l'] = rate
                        self.cache[frame]['c'] = rate
                        self.cache[frame]['v'] += amount
                        self.cache[frame]['r'].append(rate)
                        self.cache[frame]['a'].append(amount)

                        self.data[frame][-1] = {
                            'timestamp': now,
                            'utc_date': utc_timestamp_to_date(now),
                            'high': self.cache[frame]['h'],
                            'low': self.cache[frame]['l'],
                            'open': self.cache[frame]['o'],
                            'close': self.cache[frame]['c'],
                            'mean': weighted_average(self.cache[frame]['r'], self.cache[frame]['a']),
                            'volume': self.cache[frame]['v'] * rate,
                            'c_volume': self.cache[frame]['v'],
                            'amplitude': round(percent(self.cache[frame]['l'], self.cache[frame]['h']), 2)
                        }

                if new:       # добавление свечи
                    self.cache[frame]['r'] = [rate]
                    self.cache[frame]['a'] = [amount]
                    self.cache[frame]['o'] = self.cache[frame]['c'] = self.cache[frame]['h'] = self.cache[frame]['l'] = rate
                    self.cache[frame]['v'] = amount

                    self.data[frame].append({
                        'timestamp': now,
                        'utc_date': utc_timestamp_to_date(now),
                        'high': rate,
                        'low': rate,
                        'open': rate,
                        'close': rate,
                        'mean': rate,
                        'volume': amount * rate,
                        'c_volume': amount,
                        'amplitude': 0,
                    })

    def update_frame(self, candles, frame):
        again = False
        res = get_charts_formatted(self.api.get_chart(self.pair, candles, frame))
        if res:
            if self.check_charts_integrity(res, frame):
                while True:
                    if not self.lock:
                        self.lock = True
                        if len(self.data[frame]) > 2:
                            for x in range(-2, -len(res), -1):  # начинаем с предпоследней свечи!
                                for y in range(-1, -20, -1):
                                    if self.data[frame][y]['date'] == res[x]['date']:
                                        self.data[frame][y] = res[x]
                                        break
                                    if self.data[frame][y - 1]['date'] < res[x]['date'] < self.data[frame][y]['date']:
                                        self.data[frame].insert(y, res[x])
                                        break
                        else:
                            self.data[frame] = res
                            break
                    break
                self.lock = False
            else:
                again = True
                print(' get_charts не прошел проверку', candles, frame, 'ждем 30 сек')
        else:
            again = True
            print(' get_charts получил пустой ответ', candles, frame, 'ждем 30 сек')

        if again:
            print(res)
            sleep(30)
            self.update_frame(candles, frame)


def get_charts_formatted(res):
    return [{'date': int(i['date']),
             'high': float(i['high']),
             'low': float(i['low']),
             'open': float(i['open']),
             'close': float(i['close']),
             'mean': float(i['weightedAverage']),
             'volume': float(i['volume']),
             'c_volume': float(i['quoteVolume']),
             'amplitude': round(percent(float(i['low']), float(i['high'])), 2)
             } for i in res]


class Balances:
    def __init__(self):
        pass


class SimSession:
    def __init__(self):
        # self.data = pd.DataFrame(columns=['time', 'utc_date', 'type', 'rate'])
        self.data = []


class SimExchangeThread:
    def __init__(self, pair, glob, pairs, charts, session, indicators):
        self.pair = pair
        self.glob = glob
        self.pairs = pairs[pair]
        self.charts = charts[pair]
        self.session = session
        self.indicators = indicators[pair]

    def sim_detect_long_in(self):
        res = False
        # if self.indicators['5m'][]
        # if res:
        #     self.session.data.append({'time': _time, 'utc_date': _utc__date, 'rate': _rate, 'type': _type})

    def sim_detect_short_in(self):
        pass

    def sim_detect_long_out(self):
        pass

    def sim_detect_short_out(self):
        pass
