from inc.inc_functions import *
from inc.inc_system import *
import numpy as np
import talib as tb
import pandas as pd
# import scipy.signal
# from peakdetect import peakdetect
from mods.mod_indicators import SuperTrend
import math
from numba import njit
import ta.volume as ta


class Indicators:
    def __init__(self, data):
        self.data = data
        self.charts = data.charts
        self.params = data.params
        self.tools = data.params['tools']
        self.arr = {i: dict() for i in self.params['time_frames']}
        self.options = {i: dict() for i in self.params['time_frames']}
        self.run()

    def run(self):
        t1 = time()
        """
        row - списки значений индикаторов, на каждый фрейм своё значение
        points - произвольные точки с координатами
        """

        for frame in self.params['time_frames']:
            for name, config in self.tools.items():
                getattr(self, config['method'])(frame, name, config)
        t2 = time()
        print(f'Indicators generation took {to4(t2 - t1)} sec')

        # row[frame]['stoch_rsi_k'], row[frame]['stoch_rsi_d'] = tb.STOCHRSI(
        #     self.data.charts[frame]['c'][0 if full_range else -35:], timeperiod=14, fastk_period=8, fastd_period=14)
        #
        # row[frame]['stoch_f'], row[frame]['stoch_s'] = tb.STOCH(
        #     self.data.charts[frame]['h'][0 if full_range else -16:],
        #     self.data.charts[frame]['l'][0 if full_range else -16:],
        #     self.data.charts[frame]['c'][0 if full_range else -16:],
        #     fastk_period=14, slowk_period=1, slowd_period=3)

        # points[frame]['points_max_peaks'], points[frame]['points_min_peaks'] = self.peak_detect(
        #     self.data.charts[frame]['h'][0 if full_range else -5:],
        #     self.data.charts[frame]['l'][0 if full_range else -5:],
        #     self.data.charts[frame]['utc_date'][0 if full_range else -5:],
        #     self.data.charts[frame]['timestamp'][0 if full_range else -5:],
        #     self.params['time_frames'][frame],
        #     5)

    def EMA(self, frame, name, config):
        if config['input_data'] == 'm':
            h = self.data.charts[frame]['h']
            l = self.data.charts[frame]['l']
            data = np.array([(h[i] + l[i]) / 2 for i in range(len(h))])
        else:
            data = self.data.charts[frame][config['input_data']]
        self.arr[frame][name] = tb.EMA(data, config['period'])

    def TEMA(self, frame, name, config):
        data = self.data.charts[frame][config['input_data']]
        self.arr[frame][name] = tb.TEMA(data, config['period'])

    def JMA(self, frame, name, config):
        if config['input_data'] == 'm':
            h = self.data.charts[frame]['h']
            l = self.data.charts[frame]['l']
            data = [(h[i] + l[i]) / 2 for i in range(len(h))]
        else:
            data = self.data.charts[frame][config['input_data']]
        phase = config.get('phase') if config.get('phase') else 100
        power = config.get('power') if config.get('power') else 1
        self.arr[frame][name] = JMA(data, period=config['period'], phase=phase, power=power)

    def ADX(self, frame, name, config):
        data = self.data.charts[frame]
        self.arr[frame][name] = tb.ADX(data['h'], data['l'], data['c'], config['period'])

    def ATR(self, frame, name, config):
        data = self.data.charts[frame]
        self.arr[frame][name] = tb.ATR(data['h'], data['l'], data['c'], config['period'])

    def VWAP(self, frame, name, config):
        data = self.data.charts[frame]
        self.arr[frame][name] = tb.ADX(data['v'], data['h'], data['l'], config['period'])

    def MA_SPEED(self, frame: str, name: str, config: dict):
        ma = self.arr[frame][config['input_data']]
        self.arr[frame][name] = [(percent(ma[i-1], ma[i], 3) + percent(ma[i-2], ma[i-1], 3) + percent(ma[i-3], ma[i-2], 3)) / 3 for i in range(len(ma))]

    def MA_CHANNEL(self, frame: str, name: str, config: dict):
        ma = self.arr[frame][config['input_data']]
        driver_data = self.arr[frame][config['driver_data']]
        h = self.charts[frame]['h']
        l = self.charts[frame]['l']

        # ma_speed = self.arr[frame][config['driver_data']]
        # ma_upper = [y + 200 for i, y in enumerate(ma)]
        # ma_lower = [y - 200 for i, y in enumerate(ma)]
        ma_upper = [y + h[i] * driver_data[i] / 3 for i, y in enumerate(ma)]
        ma_lower = [y - 15000 * driver_data[i] for i, y in enumerate(ma)]
        # ma_upper = [y + 15000 * driver_data[i] for i, y in enumerate(ma)]
        # ma_lower = [y - 15000 * driver_data[i] for i, y in enumerate(ma)]
        self.arr[frame][name + '_u'] = ma_upper
        self.arr[frame][name + '_l'] = ma_lower

    def MA_CANDLE_RELATION(self, frame: str, name: str, config: dict):
        ma = self.arr[frame][config['input_data']]
        h = self.charts[frame]['h']
        l = self.charts[frame]['l']
        # self.arr[frame][name] = [(h[i] - m) / (m - l[i]) for i, m in enumerate(ma)]
        res = []
        for i, m in enumerate(ma):
            if l[i] > m:
                res.append(100)
                continue
            if h[i] < m:
                res.append(-100)
                continue
            above = h[i] - m
            below = m - l[i]
            total = h[i] - l[i]
            if above > below:
                res.append(int(above / total * 100) if total != 0 else 100)
            else:
                res.append(int(-below / total * 100) if total != 0 else 100)

        self.arr[frame][name] = res

    def CUSTOM_MACD(self, frame: str, name: str, config: dict):
        # MACD = EMA(CLOSE, 12) - EMA(CLOSE, 26)
        # SIGNAL = SMA(MACD, 9)
        macd = np.array(self.arr[frame]['ema_f']) - np.array(self.arr[frame]['ema_m'])
        signal = tb.EMA(macd, 7)
        colors = ['#00B519' if macd[i] > macd[i - 1] else '#ff0000' for i in range(len(macd))]
        return macd * 10000, signal * 10000, colors

    def BB_B(self, frame: str, name: str, config: dict):
        data = self.charts[frame][config['input_data']]
        u, m, l = tb.BBANDS(data, timeperiod=config['period'], nbdevup=2, nbdevdn=2, matype=1)
        b = [(val - l[i]) / (u[i] - l[i]) for i, val in enumerate(data)]
        self.arr[frame][name + '_u'], self.arr[frame][name + '_m'], self.arr[frame][name + '_l'], self.arr[frame][name + '_b'] = u, m, l, b

    def AO(self, frame: str, name: str, config: dict):
        # Awesome OScilator
        median = np.asarray([(self.charts[frame]['h'][i] - self.charts[frame]['l'][i]) / 2 for i in range(len(self.charts[frame]['h']))])
        self.arr[frame][name] = tb.SMA(median, 34) - tb.SMA(median, 5)

    def ema_diff(self, ema_1, ema_2):
        return [ema_1[i] - ema_2[i] for i in range(len(ema_1))]

    def supertrend(self, frame, period, multiplier):
        df = pd.DataFrame(
                {
                    'open': [i['open'] for i in self.charts[frame]],
                    'close': [i['close'] for i in self.charts[frame]],
                    'high': [i['high'] for i in self.charts[frame]],
                    'low': [i['low'] for i in self.charts[frame]]
                }
            )
        r = SuperTrend(df, period, multiplier, ohlc=['open', 'high', 'low', 'close'])
        return r['ST_10_1'].tolist(), r['STX_10_1'].tolist()

    def MACD(self, data, fast, slow, signal):
        # MACD = EMA(CLOSE, 12) - EMA(CLOSE, 26)
        # SIGNAL = SMA(MACD, 9)
        ema, signal, hist = tb.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        colors = ['#00B519' if hist[i] > hist[i - 1] else '#ff0000' for i in range(len(hist))]
        return ema, signal, hist, colors

    # def peaks1(self):
    #     # p, _ = find_peaks(self.np_high, prominence=1)
    #     # p = peakdetect(self.np_high['3m'], lookahead=5)
    #     # pprint(p)
    #
    #     max_peaks = p[0]
    #     min_peaks = p[1]
    #
    #     x = [self.utc_dates[max_peaks[i][0]] for i in range(len(max_peaks))]
    #     y = [max_peaks[i][1] for i in range(len(max_peaks))]
    #
    #     # x = [self.utc_dates[i] for i in p]
    #     # y = [self.np_high[i] for i in p]
    #     return {'x': x, 'y': y}

    # def peaks2(self):
    #     p, _ = scipy.signal.find_peaks(self.np_high, width=50)
    #     x = [self.utc_dates[i] for i in p]
    #     y = [self.np_high[i] for i in p]
    #     return {'x': x, 'y': y}

    # def peaks3(self):
    #     # p = scipy.signal.mlpy.findpeaks_dist(self.np_high, mindist=2.1)
    #     # p = scipy.signal.argrelextrema(self.np_high, comparator=np.greater, order=2)
    #     x = [self.utc_dates[i] for i in p]
    #     y = [self.np_high[i] for i in p]
    #
    #     return {'x': x, 'y': y}

    def find_maximums(self, distance=50):
        res = {'x': [], 'y': []}
        last_peak = 0
        for i in range(len(self.np_high)):
            try:
                # x = [z for h in range(i-distance, i+distance)]) if self.np_high[i] > max([self.np_high[h] for z in range(len(self.np_high))]
                if self.np_high[i] >= max([self.np_high[z] for z in range(i-distance, i+distance)]):
                    if i > last_peak + distance:
                        res['x'].append(self.utc_dates[i])
                        res['y'].append(self.np_high[i])
                        last_peak = i
            except IndexError:
                pass

        return res

    def HA(self, o, h, l, c):
        df = pd.DataFrame([o, h, l, c], index=['Open', 'High', 'Low', 'Close']).T
        df['HA_Close'] = (df['Open'] + df['High'] + df['Low'] + df['Close']) / 4

        idx = df.index.name
        df.reset_index(inplace=True)

        ha_close_values = df['HA_Close'].values

        length = len(df)
        ha_open = np.zeros(length, dtype=float)
        ha_open[0] = (df['Open'][0] + df['Close'][0]) / 2

        for i in range(0, length - 1):
            ha_open[i + 1] = (ha_open[i] + ha_close_values[i]) / 2

        df['HA_Open'] = ha_open

        df['HA_High'] = df[['HA_Open', 'HA_Close', 'High']].max(axis=1)
        df['HA_Low'] = df[['HA_Open', 'HA_Close', 'Low']].min(axis=1)
        return df['HA_Open'].tolist(), df['HA_High'].tolist(), df['HA_Low'].tolist(), df['HA_Close'].tolist()

    # def heiken_ashi(self, o, h, l, c):
    #     ha_close = (o + h + l + c) / 4
    #     ha_open = (old_o + old_c) / 2
    #     elements = np.array([h, l, ha_open, ha_close])
    #     ha_high = elements.max(h)
    #     ha_low = elements.min(l)
    #     out = np.array([ha_close, ha_open, ha_high, ha_low])
    #     return out

    # def ichimoku(self):
    #     d = pd.DataFrame(
    #         {
    #             'open': [i['open'] for i in self.data.charts],
    #             'close': [i['close'] for i in self.data.charts],
    #             'high': [i['high'] for i in self.data.charts],
    #             'low': [i['low'] for i in self.data.charts]
    #         },
    #         index=self.timestamps,
    #     )
    #
    #     # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
    #     nine_period_high = d['high'].rolling(window=9).max()
    #     nine_period_low = d['low'].rolling(window=9).min()
    #     d['conversion'] = (nine_period_high + nine_period_low) / 2
    #
    #     # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
    #     period26_high = d['high'].rolling(window=26).max()
    #     period26_low = d['low'].rolling(window=26).min()
    #     d['base'] = (period26_high + period26_low) / 2
    #
    #     last_time = d.index[-1]
    #     timedelta = d.index[1] - d.index[0]
    #     d = d.append(pd.DataFrame(index=list(range(last_time + timedelta, (last_time + timedelta) + timedelta * 26, timedelta))))
    #
    #     # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2))
    #     d['senkou_span_a'] = ((d['conversion'] + d['base']) / 2).shift(26)
    #
    #     # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
    #     period52_high = d['high'].rolling(window=52).max()
    #     period52_low = d['low'].rolling(window=52).min()
    #     d['senkou_span_b'] = ((period52_high + period52_low) / 2).shift(26)
    #
    #     # The most current closing price plotted 26 time periods behind (optional)
    #     d['lagging'] = d['close'].shift(-26)
    #
    #     # for i in range(len(d.index)-1):
    #     #     if d.index[i] + 300 != d.index[i + 1]:
    #     #         print('ERROR in', i, d.index[i], d.index[i + 1])
    #
    #     return {
    #             'date': [utc_timestamp_to_date(i) for i in d.index.tolist()],
    #             'conversion': d['conversion'].tolist(),
    #             'base': d['base'].tolist(),
    #             'senkou_span_a': d['senkou_span_a'].tolist(),
    #             'senkou_span_b': d['senkou_span_b'].tolist(),
    #             'lagging': d['lagging'].tolist(),
    #             }


def peak_detect(h, l, utc, timestamp, frame_size, radius):
    highs = []
    lows = []
    for i in range(radius, len(h)):
        if h[i] == max(h[i - radius:i + radius]):
            try:
                if timestamp[i] - highs[-1]['timestamp'] >= radius * frame_size:
                    highs.append({'x': utc[i], 'y': h[i], 'timestamp': timestamp[i]})
            except IndexError:
                highs.append({'x': utc[i], 'y': h[i], 'timestamp': timestamp[i]})
        if l[i] == min(l[i - radius:i + radius]):
            try:
                if timestamp[i] - lows[-1]['timestamp'] >= radius * frame_size:
                    lows.append({'x': utc[i], 'y': l[i], 'timestamp': timestamp[i]})
            except IndexError:
                lows.append({'x': utc[i], 'y': l[i], 'timestamp': timestamp[i]})
    return highs, lows


# @njit
def JMA(values, period=15, phase=100, power=2):
    # Jurik Moving Average
    beta = 0.45 * (period - 1) / (0.45 * (period - 1) + 2)
    alpha = pow(beta, power)
    phase_ratio = 0.5 if phase < -100 else 2.5 if phase > 100 else phase / 100 + 1.5
    ma1 = det0 = det1 = jma = 0
    res = []
    for value in values:
        ma1 = (1 - alpha) * value + alpha * ma1
        det0 = (value - ma1) * (1 - beta) + beta * det0
        ma2 = ma1 + phase_ratio * det0
        det1 = (ma2 - jma) * pow(1 - alpha, 2) + pow(alpha, 2) * det1
        jma = jma + det1
        res.append(jma)
    return res


def JMA_BANDS(jma, price, period=10, n=2):
    # band_up = []
    # band_down = []
    band = n * np.std(price[-period:])
    band_up = jma + band
    band_down = jma - band
    # try:
    #     for i in range(len(price)):
    #         # band = n * math.sqrt(sum([pow(price[x] - jma[x], 2) for x in range(i - period, i)]) / period)
    #         # band = n * math.sqrt(math.mean([pow(price[x] - jma[x], 2) for x in range(i - period, i)]) / period)
    #         # band = price[-period:] - jma[-period:]
    #         band = n * np.std(price[-period:])
    #         band_up.append(jma[i] + band)
    #         band_down.append(jma[i] - band)

    # except IndexError:
    #     pass
    return band_up, band_down


# def EMA_speed(ema_f, ema_s):  # скорость изменения EMA
#     lst = []
#     # step = 1 / period
#     # for x in range(len(ema)):
#     #     try:
#     #         values = [percent(ema[i-1], ema[i]) for i in range(-period + x + 1, x + 1)]
#     #         weights = [i * step for i in range(-period + x + 1, x + 1)]
#     #         lst.append(round(weighted_average(values, weights), 4))
#     #         # lst.append(sum(values) / period)
#     #     except IndexError:
#     #         lst.append(0)
#
#     for i in range(len(ema_f)):
#         try:
#             lst.append(percent(ema_f[i-1], ema_f[i]) / (percent(ema_f[i], ema_s[i])))
#         except IndexError:
#             lst.append(0)
#     return lst, ['#00B519' if lst[i] > lst[i - 1] else '#ff0000' for i in range(len(lst))]


def EMA_diff(ema_fast, ema_slow):  # гистограмма разниц EMA
    # hist = ema_fast - ema_slow
    # return hist, ['#00B519' if hist[i] > hist[i - 1] else '#ff0000' for i in range(len(hist))]
    lst = []
    for i in range(len(ema_fast)):
        try:
            lst.append(percent(ema_slow[i], ema_fast[i]))
        except IndexError:
            lst.append(0)
    return lst, ['#00B519' if lst[i] > lst[i - 1] else '#ff0000' for i in range(len(lst))]
#
#
# def EMA_trend_prob(ema, arr_high, arr_low, period=30):  # % свечей выше или ниже EMA 100 за период
#     lst = []
#     for x in range(len(ema)):
#         try:
#             tmp = []
#             for i in range(-period + x + 1, x + 1):
#                 if ema[i] < arr_low[i]:
#                     tmp.append(100)
#                 elif ema[i] > arr_high[i]:
#                     tmp.append(-100)
#                 else:
#                     tmp.append(0)
#             lst.append(int(sum(tmp) / len(tmp)))
#         except IndexError:
#             lst.append(0)
#     return lst
#
#
# def find_minimums(lst, i, arr_close, macd):
#

#     if lst[i]['low'] <= lst[i - 1]['low'] and lst[i]['low'] <= lst[i - 2]['low'] and lst[i]['low'] <= lst[i - 3]['low']:
#         if lst[i]['low'] <= lst[i + 1]['low'] and lst[i]['low'] <= lst[i + 2]['low']:
#             # if percent(lst[i]['low'], max(lst[i + 1]['high'], lst[i + 2]['high'], lst[i + 3]['high'])) >= 0.2:
#             if macd[i] < 0:
#                 return True
#     else:
#         return False


def HMA(dat, period=100):
    return tb.WMA(2 * tb.WMA(dat, period / 2) - tb.WMA(dat, period), round(math.sqrt(period)))

# @njit
# def vwap(volume, high, low):
#     return np.cumsum(volume * (high + low) / 2) / np.cumsum(volume)


def vwap(h, l, c, v):
    res = ta.volume_weighted_average_price(
        pd.Series(h),
        pd.Series(l),
        pd.Series(c),
        pd.Series(v),
        window=14,
        fillna=False)
    return res.tolist()
