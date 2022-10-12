from inc.inc_functions import *
from inc.inc_system import *
import numpy as np
import talib as tb
import pandas as pd
import scipy.signal
from peakdetect import peakdetect
from mods.mod_indicators import SuperTrend
import math


class Indicators:
    def __init__(self, data):
        self.data = data
        self.charts = data.charts
        self.params = data.params
        self.np_open = {i: [] for i in self.params['time_frames']}
        self.np_close = {i: [] for i in self.params['time_frames']}
        self.np_high = {i: [] for i in self.params['time_frames']}
        self.np_low = {i: [] for i in self.params['time_frames']}
        self.utc_dates = {i: [] for i in self.params['time_frames']}
        self.timestamps = {i: [] for i in self.params['time_frames']}
        self.fractals = {i: {} for i in self.params['time_frames']}
        self.arr = {i: dict() for i in self.params['time_frames']}
        self.options = {i: dict() for i in self.params['time_frames']}
        self.update_indicators()

    def update_indicators(self):
        for frame in self.params['time_frames']:
            self.np_open[frame] = np.array([i['open'] for i in self.charts[frame]])
            self.np_close[frame] = np.array([i['close'] for i in self.charts[frame]])
            self.np_high[frame] = np.array([i['high'] for i in self.charts[frame]])
            self.np_low[frame] = np.array([i['low'] for i in self.charts[frame]])
            self.utc_dates[frame] = [i['utc_date'] for i in self.charts[frame]]
            self.timestamps[frame] = [i['timestamp'] for i in self.charts[frame]]

            # self.arr[frame]['stoch_rsi_k'], self.arr[frame]['stoch_rsi_d'] = tb.STOCHRSI(self.np_close[frame], timeperiod=14, fastk_period=3, fastd_period=3, fastd_matype=2)

            # self.arr[frame]['bb_u_2'], self.arr[frame]['bb_m_2'], self.arr[frame]['bb_l_2'] = tb.BBANDS(self.np_close[frame], timeperiod=16, nbdevup=2, nbdevdn=2, matype=0)
            self.arr[frame]['ema_f'] = JMA(self.np_close[frame], period=self.params['ema_f'], phase=self.params['ema_f_phase'], power=self.params['ema_f_power'])
            self.arr[frame]['ema_m'] = JMA(self.np_close[frame], period=self.params['ema_m'], phase=self.params['ema_m_phase'], power=self.params['ema_m_power'])
            self.arr[frame]['jma_band_up'], self.arr[frame]['jma_band_down'] = JMA_BANDS(self.arr[frame]['ema_m'], self.np_close[frame], 20, 2)
            # self.arr[frame]['ema_f'] = HMA(self.np_close[frame], self.params['ema_f'])
            # self.arr[frame]['ema_m'] = HMA(self.np_close[frame], self.params['ema_m'])
            # self.arr[frame]['ema_s'] = tb.EMA(self.np_close[frame], timeperiod=self.params['ema_s'])
            # self.arr[frame]['ema_xs'] = tb.EMA(self.np_close[frame], timeperiod=self.params['ema_xs'])

            # self.arr[frame]['jma_macd'], self.arr[frame]['jma_signal'], self.arr[frame]['jma_colors'] = self.JMA_MACD(frame)

            # self.arr[frame]['kama'] = tb.KAMA(self.np_close[frame], timeperiod=9)
            # self.arr[frame]['supertrend'], self.arr[frame]['supertrend1'] = self.supertrend(frame, 10, 1)
            # self.arr[frame]['ema_dif'], self.arr[frame]['ema_dif_color'] = EMA_diff(self.arr[frame]['ema_f'], self.arr[frame]['ema_m'])
            # self.arr[frame]['atr'] = tb.ATR(self.np_high[frame], self.np_low[frame], self.np_close[frame], timeperiod=14)

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
        # print(r['ATR_10'].tolist())
        return r['ST_10_1'].tolist(), r['STX_10_1'].tolist()

    def MACD(self, data, fast, slow, signal):
        # MACD = EMA(CLOSE, 12) - EMA(CLOSE, 26)
        # SIGNAL = SMA(MACD, 9)
        ema, signal, hist = tb.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        colors = ['#00B519' if hist[i] > hist[i - 1] else '#ff0000' for i in range(len(hist))]
        return ema, signal, hist, colors

    def peaks1(self):
        # p, _ = find_peaks(self.np_high, prominence=1)
        p = peakdetect(self.np_high, lookahead=5)
        # pprint(p)

        max_peaks = p[0]
        min_peaks = p[1]

        x = [self.utc_dates[max_peaks[i][0]] for i in range(len(max_peaks))]
        y = [max_peaks[i][1] for i in range(len(max_peaks))]

        # x = [self.utc_dates[i] for i in p]
        # y = [self.np_high[i] for i in p]

        return {'x': x, 'y': y}

    def peaks2(self):
        p, _ = scipy.signal.find_peaks(self.np_high, width=50)
        x = [self.utc_dates[i] for i in p]
        y = [self.np_high[i] for i in p]

        return {'x': x, 'y': y}

    def peaks3(self):
        p = scipy.signal.mlpy.findpeaks_dist(self.np_high, mindist=2.1)
        # p = scipy.signal.argrelextrema(self.np_high, comparator=np.greater, order=2)
        x = [self.utc_dates[i] for i in p]
        y = [self.np_high[i] for i in p]

        return {'x': x, 'y': y}

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

    def williams_fractals(self, highs, lows, timestamps, utc_dates):
        up = down = {'x': [], 'y': [], 'timestamp': []}
        up_timestamp = 0
        down_timestamp = 0

        for i in range(len(highs)):
            try:
                if highs[i - 6] < highs[i - 5] < highs[i - 4]:
                    if highs[i - 4] > highs[i - 3] > highs[i - 2]:
                        if up_timestamp != timestamps[i - 4]:
                            up['x'].append(utc_dates[i - 4])
                            up['y'].append(add_percent(highs[i - 4], 0.3))
                            up['timestamp'].append(timestamps[i - 4])
                            up_timestamp = timestamps[i - 4]

                if lows[i - 6] > lows[i - 5] > lows[i - 4]:
                    if lows[i - 4] < lows[i - 3] < lows[i - 2]:
                        if down_timestamp != timestamps[i - 4]:
                            down['x'].append(utc_dates[i - 4])
                            down['y'].append(add_percent(lows[i - 4], -0.3))
                            down['timestamp'].append(timestamps[i - 4])
                            down_timestamp = timestamps[i - 4]
            except IndexError:
                pass
        return up, down

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

    def JMA_MACD(self, frame):
        # MACD = EMA(CLOSE, 12) - EMA(CLOSE, 26)
        # SIGNAL = SMA(MACD, 9)
        macd = np.array(self.arr[frame]['ema_f']) - np.array(self.arr[frame]['ema_m'])
        signal = tb.DEMA(macd, 7)
        colors = ['#00B519' if macd[i] > macd[i - 1] else '#ff0000' for i in range(len(macd))]
        return macd * 10000, signal * 10000, colors


def JMA(values, period=20, phase=100, power=2):
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


def JMA_BANDS(jma, price, period=20, n=2):
    band_up = []
    band_down = []

    try:
        for i in range(len(price)):
            band = n * math.sqrt(sum([pow(price[x] - jma[x], 2) for x in range(i - period, i)]) / period)
            band_up.append(jma[i] + band)
            band_down.append(jma[i] - band)

    except IndexError:
        pass
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







# /    DMA - Dickson Moving Average
# //    Blends the result of a Hull Moving Average with
# //    an Ehlers "Zero Lag" calculation.
#
# inputs:
#     price(numericseries);
#
# vars:
#     alpha(0),
#     gain(0),
#     bestGain(0),
#     ec(0),
#     hull(0),
#     error(0),
#     leastError(0),
#     ema(0);
#
# const:
#     hullPeriod(7),
#     emaLength(20),
#     emaGainLimit(50);
#
# alpha = 2 / (emaLength + 1);
# ema = alpha * price + (1 - alpha) * ema[1];
# leastError = 1000000;
#
# for value1 = -emaGainLimit to emaGainLimit begin
#     gain = value1 / 10;
#     ec = alpha * ( ema + gain * (price - ec[1]) ) + (1 - alpha) * ec[1];
#     error = price - ec;
#     if absValue(error) < leastError then begin
#         leastError = absValue(error);
#         bestGain = gain;
#     end;
# end;
#
# ec = alpha * ( ema + bestGain * (price - ec[1]) ) + (1 - alpha) * ec[1];
# hull = HMA( price, hullPeriod );
#
# _DMA = (ec + hull) / 2;
