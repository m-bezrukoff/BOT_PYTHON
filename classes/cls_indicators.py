from config import *
from inc.inc_system import sleep, time,  utc_timestamp_to_date, local_timestamp_to_date, find_candle_start_time, to8
from PyQt6.QtCore import QThread

import talib
import numpy as np
import pandas as pd
from numba import njit
# from ta.trend import vortex_indicator_pos, vortex_indicator_neg


class Indicators(QThread):
    def __init__(self, pair, pairs, charts, public_trades, private_trades, socket_server):
        super().__init__()
        self.pair = pair
        self.glob = pairs[pair].glob
        self.log = pairs[pair].log
        self.socket_server = socket_server
        self.pairs = pairs[pair]
        self.charts = charts[pair]
        self.public_trades = public_trades[pair]
        self.private_trades = private_trades[pair]

        self.list_high = {i: [] for i in conf_time_frames}
        self.list_low = {i: [] for i in conf_time_frames}
        self.list_open = {i: [] for i in conf_time_frames}
        self.list_close = {i: [] for i in conf_time_frames}
        self.list_volume = {i: [] for i in conf_time_frames}
        self.list_date = {i: [] for i in conf_time_frames}

        self.arr_open = {i: [] for i in conf_time_frames}
        self.arr_close = {i: [] for i in conf_time_frames}
        self.arr_high = {i: [] for i in conf_time_frames}
        self.arr_low = {i: [] for i in conf_time_frames}
        self.arr_volume = {i: [] for i in conf_time_frames}

        self.buy_points = {}
        self.trade_points = {'buy': {'x': [], 'y': []}, 'sell': {'x': [], 'y': []}}

        # self.temp = load_zipped_pickle('log/test_trades_' + self.pair + '.dat')

        self.tma_s = {i: [] for i in conf_time_frames}
        self.tma_f = {i: [] for i in conf_time_frames}
        self.tma_m = {i: [] for i in conf_time_frames}

        # self.ema_diff = {i: [] for i in conf_time_frames}
        # self.ema_diff_c = {i: [] for i in conf_time_frames}

        self.macd_m = {i: [] for i in conf_time_frames}
        self.macd_s = {i: [] for i in conf_time_frames}
        self.macd_h = {i: [] for i in conf_time_frames}
        self.macd_c = {i: [] for i in conf_time_frames}

        self.bb_u_2 = {i: [] for i in conf_time_frames}
        self.bb_m_2 = {i: [] for i in conf_time_frames}
        self.bb_l_2 = {i: [] for i in conf_time_frames}

        self.vortex = {i: [] for i in conf_time_frames}

        self.peaks = {i: {'peaks': {'x': [], 'y': []}, 'troughs': {'x': [], 'y': []}} for i in conf_time_frames}
        self.clusters = {i: [] for i in conf_time_frames}
        self.cluster_colors = ['#ff0000', '#ff0000', '#ff0000', '#ffd63f', '#ffd63f', '#ffd63f', '#ffd63f', '#27ff12', '#27ff12', '#27ff12', '#27ff12']
        self.time_last_export = 0
        # self.cluster_colors = ['#27ff12', '#27ff12', '#27ff12', '#ffd63f', '#ffd63f', '#ffd63f', '#ffd63f', '#ff0000', '#ff0000', '#ff0000', '#ff0000']

    def update_indicators(self):
        # массив обновляется из chart_create_from_trades
        for frame in conf_time_frames:
            self.list_high[frame] = [i['high'] for i in self.charts.data[frame]]
            self.arr_high[frame] = np.array(self.list_high[frame])

            self.list_low[frame] = [i['low'] for i in self.charts.data[frame]]
            self.arr_low[frame] = np.array(self.list_low[frame])

            self.list_open[frame] = [i['open'] for i in self.charts.data[frame]]
            self.arr_open[frame] = np.array(self.list_open[frame])

            self.list_close[frame] = [i['close'] for i in self.charts.data[frame]]
            self.arr_close[frame] = np.array(self.list_close[frame])

            self.list_volume[frame] = [i['volume'] for i in self.charts.data[frame]]
            self.arr_volume[frame] = np.array(self.list_volume[frame])

            self.list_date[frame] = [i['utc_date'] for i in self.charts.data[frame]]

            # self.tma_s[frame] = talib.TEMA(self.arr_close[frame], timeperiod=50)
            self.tma_m[frame] = talib.TEMA(self.arr_close[frame], timeperiod=21)
            self.tma_f[frame] = talib.TEMA(self.arr_close[frame], timeperiod=8)

            self.macd_m[frame], self.macd_s[frame], self.macd_h[frame], self.macd_c[frame] = self.macd(frame, fast=12, slow=21, signal=9)
            self.bb_u_2[frame], self.bb_m_2[frame], self.bb_l_2[frame] = talib.BBANDS(self.arr_close[frame], timeperiod=16, nbdevup=2, nbdevdn=2, matype=0)

            # self.ema_f[frame] = talib.WMA(self.arr_close[frame], timeperiod=10)
            # self.ema_s[frame] = talib.WMA(self.arr_close[frame], timeperiod=16)
            # self.vortex[frame] = self.vortex_indicator(frame)
            # self.ema_f[frame] = self.ema(frame, 10)
            # self.ema_s[frame] = self.ema(frame, 16)
            # self.ema_diff = self.ema_f - self.ema_s
            # self.ema_diff[frame], self.ema_diff_c[frame] = self.ema_difference(frame)
            # self.tma, self.wma, self.tma_hist, self.tma_colors = self.TMA_DIFF(7)
            # self.support = self.support_lines()
            if conf_indicators_clusters:
                self.clusters[frame] = self.export_clusters(frame)
            # self.peaks = scipy.signal.find_peaks_cwt(self.arr_high[frame], np.arange(1, 2), max_distances=np.arange(1, 2)*2)
            if conf_indicators_peaks:
                self.peaks[frame] = self.detect_peaks(frame)

    # @show_taken_time
    def export_graphics_data(self):
        if time() - self.time_last_export > conf_graph_rotation_delay:
            if self.glob.display_pair == self.pair:
                limit = conf_display_candles     # количество выводимых свечей на графике
                pair = self.glob.display_pair
                frame = self.glob.display_timeframe
                msg = {
                    'frames': [i for i in conf_time_frames],
                    'time': local_timestamp_to_date(),
                    'pair': pair,
                    'bid': self.pairs.bid_rate,
                    'ask': self.pairs.ask_rate,
                    'rate': self.pairs.rate,
                    'date': self.list_date[frame][-limit:],
                    'open': self.list_open[frame][-limit:],
                    'close': self.list_close[frame][-limit:],
                    'high': self.list_high[frame][-limit:],
                    'low': self.list_low[frame][-limit:],
                    'volume': self.list_volume[frame][-limit:],
                    'amplitude': ['amplitude {}%'.format(i['amplitude']) for i in self.charts.data[frame][-limit:]],

                    'macd_m': self.macd_m[frame][-limit:].tolist(),
                    'macd_h': self.macd_h[frame][-limit:].tolist(),
                    'macd_c': self.macd_c[frame][-limit:],
                    'macd_s': self.macd_s[frame][-limit:].tolist(),

                    'tma_f': self.tma_f[frame][-limit:].tolist(),
                    'tma_m': self.tma_m[frame][-limit:].tolist(),
                    # 'tma_s': self.tma_s[frame][-limit:].tolist(),

                    'bb_u_2': self.bb_u_2[frame][-limit:].tolist(),
                    'bb_m_2': self.bb_m_2[frame][-limit:].tolist(),
                    'bb_l_2': self.bb_l_2[frame][-limit:].tolist(),

                    'clusters': self.clusters[frame],
                    'trade_points': self.update_trade_points(frame),
                    # 'peaks': self.peaks[frame],
                    # 'vortex': {'pos': self.vortex[frame]['pos'][-limit:], 'neg': self.vortex[frame]['neg'][-limit:], 'dif': self.vortex[frame]['dif'][-limit:]}
                }
                self.socket_server.send(msg)

    def detect_peaks(self, frame, rng=2):
        peaks = {'x': [], 'y': []}
        troughs = {'x': [], 'y': []}

        for i in range(2, len(self.list_high[frame])):
            try:
                if max(self.list_high[frame][i-1-rng:i-1]) <= self.list_high[frame][i-1] > self.list_high[frame][i]:
                    # if self.ema_f[frame][i-2] <= self.ema_f[frame][i-1] > self.ema_f[frame][i]:
                    peaks['y'].append(self.list_high[frame][i-1])
                    peaks['x'].append(self.list_date[frame][i-1])

                if min(self.list_low[frame][i-1-rng:i-1]) >= self.list_low[frame][i-1] < self.list_low[frame][i]:
                    troughs['y'].append(self.list_low[frame][i-1])
                    troughs['x'].append(self.list_date[frame][i-1])
            except Exception:
                pass
        return {'peaks': peaks, 'troughs': troughs}

    def update_trade_points(self, frame):
        to = int(time())
        fr = to - conf_display_candles * conf_time_frames[frame]
        x = {'open': {'x': [], 'y': [], 'marker': []}, 'close': {'x': [], 'y': [], 'marker': []}}
        # for i in range(-1, -len(self.private_trades.data), -1):
        #     if self.private_trades.data[i]['date'] >= fr:
        #         date = utc_timestamp_to_date(find_candle_start_time(self.private_trades.data[i]['date'], conf_time_frames[frame]))
        #         x[self.private_trades.data[i]['type']]['x'].append(date)
        #         x[self.private_trades.data[i]['type']]['y'].append(self.private_trades.data[i]['rate'])
        # return x

        # for i in range(-1, -len(self.temp), -1):
        #     x[self.temp[i]['type']]['x'].append(utc_timestamp_to_date(find_candle_start_time(self.temp[i]['time'], conf_time_frames[frame])))
        #     x[self.temp[i]['type']]['y'].append(self.temp[i]['rate'])
        #     x[self.temp[i]['type']]['marker'].append(self.temp[i]['marker'])
        # return x

    def export_clusters(self, frame):
        def get_cluster_icon_size(a, b):
            return int(a / b * 20)

        res = {'x': [], 'y': [], 'color': [], 'size': []}
        clusters = self.public_trades.clusters[frame]
        for i in clusters:
            if i['rates']:
                if i['timestamp'] >= self.public_trades.data_start_time[frame]:
                    for y in i['rates']:
                        size = get_cluster_icon_size(i[y]['sum']['amount'], self.public_trades.stat_max_vol[frame])
                        if size > 2:
                            res['x'].append(i['date'])
                            res['y'].append(y + self.public_trades.rate_step[frame] / 2)
                            res['color'].append(self.cluster_colors[int(i[y]['diff']['amount_percent'] / 10)])
                            res['size'].append(size)
        return res

    def ema(self, frame, period=2):
        return talib.EMA(self.arr_close[frame], timeperiod=period)

    def tema(self, frame, period=34):
        return talib.TEMA(self.arr_close[frame], timeperiod=period)

    def macd(self, frame, fast=12, slow=26, signal=7):
        macd, signal, hist = talib.MACD(self.arr_close[frame], fastperiod=fast, slowperiod=slow,
                                        signalperiod=signal)
        colors = ['#00B519' if hist[i] > hist[i - 1] else '#ff0000' for i in range(len(hist))]
        return macd * 10, signal * 10, hist * 10, colors

    @njit
    def vwap(self, volume, high, low):
        return np.cumsum(volume[:] * (high + low) / 2) / np.cumsum(volume)

    # def squeeze(self):
    #     df['20sma'] = df['Close'].rolling(window=20).mean()
    #     df['stddev'] = df['Close'].rolling(window=20).std()
    #     df['lower_band'] = df['20sma'] - (2 * df['stddev'])
    #     df['upper_band'] = df['20sma'] + (2 * df['stddev'])
    #
    #     df['TR'] = abs(df['High'] - df['Low'])
    #     df['ATR'] = df['TR'].rolling(window=20).mean()
    #
    #     df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
    #     df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

    def vortex_indicator(self, frame, period=14):
        _high = pd.Series(self.list_high[frame])
        _low = pd.Series(self.list_low[frame])
        _close = pd.Series(self.list_close[frame])
        _fillna = False

        def _true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series) -> pd.Series:
            tr1 = high - low
            tr2 = (high - prev_close).abs()
            tr3 = (low - prev_close).abs()
            res = pd.DataFrame(data={"tr1": tr1, "tr2": tr2, "tr3": tr3}).max(axis=1)
            return res

        close_shift = _close.shift(1, fill_value=_close.mean())
        true_range = _true_range(_high, _low, close_shift)
        min_periods = 0 if _fillna else period
        trn = true_range.rolling(period, min_periods=min_periods).sum()
        vmp = np.abs(_high - _low.shift(1))
        vmm = np.abs(_low - _high.shift(1))

        vortex_pos = vmp.rolling(period, min_periods=min_periods).sum() / trn
        vortex_neg = vmm.rolling(period, min_periods=min_periods).sum() / trn
        diff = vortex_pos - vortex_neg

        # vortex_neg = vortex_indicator_neg(_high, _low, _close, window=14, fillna=False).tolist()
        # vortex_pos = vortex_indicator_pos(_high, _low, _close, window=14, fillna=False).tolist()
        return {'pos': vortex_pos.tolist(), 'neg': vortex_neg.tolist(), 'dif': diff.tolist()}


#   Vortex Indicator:
# def vortex(df, n):
#     i = 0
#     tr = [0]
#     vm = [0]
#     while i < df.index[-1]:
#         tr.append(max(df.get_value(i + 1, 'high'), df.get_value(i, 'close')) - min(df.get_value(i + 1, 'low'), df.get_value(i, 'close')))
#         vm.append(abs(df.get_value(i + 1, 'high') - df.get_value(i, 'low')) - abs(df.get_value(i + 1, 'low') - df.get_value(i, 'high')))
#         i = i + 1
#     vi = pd.Series(pd.rolling_sum(pd.Series(vm), n) / pd.rolling_sum(pd.Series(tr), n), name='Vortex_' + str(n))
#     df = df.join(vi)
#     return df

    # def RSI(self, period=7):
    #     return talib.RSI(self.arr_close, timeperiod=period)
    #
    # def CCI(self, period=60):
    #     return talib.CCI(self.arr_high, self.arr_low, self.arr_close, timeperiod=period)
    #
    # def STOCH(self, typ='K'):
    #     slowk, slowd = talib.STOCH(self.arr_high, self.arr_low, self.arr_close,
    #                                fastk_period=14, slowk_period=1, slowd_period=3)
    #     if typ == 'K':
    #         return slowk
    #     if typ == 'D':
    #         return slowd

    # def SAR(self):
    #     return talib.SAR(self.arr_close, self.arr_low, acceleration=0.01, maximum=0.2)

    # def TMA_DIFF(self, period=5):
    #     tma = talib.TEMA(self.arr_close, timeperiod=period)
    #     wma = talib.WMA(self.arr_close, timeperiod=period)
    #     tma_hist = (tma - wma) * 10000
    #     tma_colors = ['#00B519' if tma_hist[i] > tma_hist[i - 1] else '#ff0000' for i in range(len(tma_hist))]
    #     return tma, wma, tma_hist, tma_colors

    # Get the Peaks and Troughs
    # doublediff = diff(sign(diff(arr_high)))
    # peaks = where(doublediff == -2)[0] + 1
    #
    # doublediff2 = diff(sign(diff(-1 * arr_low)))
    # troughs = where(doublediff2 == -2)[0] + 1

    # return arr_high
