from inc.inc_functions import percent, add_percent, weighted_average
from inc.inc_system import to2
from statistics import mean


class Job:
    def __init__(self, indicators):
        self.indicators = []
        self.params = self.indicators.data.params
        self.total_candles = len(self.indicators.timestamps)
        self.points = {'open': {}, 'close': {}}

    def run(self, indicators):
        self.indicators = indicators
        self.tma_strategy_find_open_long_by_tradebook('5m')
        # self.tma_strategy_find_open_short('5m')
        # self.tma_strategy_find_close_long('5m')

    def append_point(self, action, i, typ, rate=None, marker=None):
        self.points[action][self.indicators.timestamps[i]] = {
            'x': self.indicators.utc_dates[i],
            'y': rate if rate else mean([self.indicators.np_high[i], self.indicators.np_low[i]]),
            'type': typ,
            'marker': marker if marker else 8,
        }

    def append_point_by_tradebook(self, frame, action, typ, rate, marker=None):
        self.points[action][self.indicators.timestamps[frame][-1]] = {
            'x': self.indicators.utc_dates[frame][-1],
            'y': rate,
            'type': typ,
            'marker': marker if marker else 8,
        }

    def tma_strategy_find_open_long_by_tradebook(self, frame):
        bb_m_2 = self.indicators.arr[frame]['bb_m_2']
        tma_f = self.indicators.arr[frame]['tma_f']
        charts = self.indicators.data.charts[frame]
        try:
            if percent(tma_f[-3], tma_f[-2]) < 0:
                if percent(tma_f[-2], tma_f[-1]) > 0:
                    if bb_m_2[-1] > tma_f[-1]:
                        print('{} --------- {} {}'.format(
                            charts[-1]['utc_date'],
                            to2(percent(tma_f[-3], tma_f[-2])),
                            to2(percent(tma_f[-2], tma_f[-1]))
                        ))
                        # print('tma_f: {} %  {} %'.format(to2(percent(tma_f[-3], tma_f[-2])), to2(percent(tma_f[-2], tma_f[-1]))))
                        self.append_point_by_tradebook(frame, 'open', 'long', charts[-1]['close'], marker=9)
        except IndexError:
            pass

        # print('enter points tma_strategy_find_open_long:', charts[-1]['utc_date'], 'candles:', len(charts))

    def tma_strategy_find_open_long(self, frame, quiet=False):
        bb_m_2 = self.indicators.arr[frame]['bb_m_2']
        tma_f = self.indicators.arr[frame]['tma_f']
        charts = self.indicators.data.charts[frame]
        try:
            print(percent(tma_f[-2], tma_f[-1]))
        except IndexError:
            pass
        counter = 0
        for i in range(self.total_candles):
            try:
                if percent(tma_f[i - 2], tma_f[i - 1]) < 0:
                    if percent(tma_f[i - 1], tma_f[i]) > 0:
                        if bb_m_2[i] > tma_f[i]:
                            print('{} -------------------------------'.format(charts[i]['utc_date']))
                            print('tma_f: {} %  {} %'.format(to2(percent(tma_f[i - 2], tma_f[i - 1])), to2(percent(tma_f[i - 1], tma_f[i]))))
                            self.append_point('open', i, 'long', marker=9)
                            counter += 1
            except Exception as e:
                pass
                # print('error', e)
        if not quiet:
            if counter:
                print('enter points tma_strategy_find_open_long:', counter, 'candles:', len(charts))

    def tma_strategy_find_close_long(self, frame, quiet=False):
        tma_f = self.indicators.arr[frame]['tma_f']
        charts = self.indicators.data.charts[frame]
        counter = 0
        for i in range(self.total_candles):
            try:
                if percent(tma_f[i - 2], tma_f[i - 1]) >= 0 > percent(tma_f[i - 1], tma_f[i]):
                    self.append_point('close', i, 'long', rate=add_percent(charts[i]['high'], -0.2), marker=4)
                    counter += 1
            except Exception as e:
                pass
        if not quiet:
            if counter:
                print('exit points tma_strategy_find_close_long:', counter)

    def tma_strategy_find_open_short(self, frame, quiet=False):
        bb_m_2 = self.indicators.arr[frame]['bb_m_2']
        tma_f = self.indicators.arr[frame]['tma_f']
        charts = self.indicators.data.charts[frame]
        counter = 0
        for i in range(self.total_candles):
            try:
                if percent(tma_f[i - 2], tma_f[i - 1]) > 0:
                    if percent(tma_f[i - 1], tma_f[i]) < 0:
                        if bb_m_2[i] < tma_f[i]:
                            print('{} -------------------------------'.format(charts[i]['utc_date']))
                            print('tma_f: {} %  {} %'.format(to2(percent(tma_f[i - 2], tma_f[i - 1])), to2(percent(tma_f[i - 1], tma_f[i]))))
                            self.append_point('open', i, 'short', marker=10)
                            counter += 1
            except Exception as e:
                pass
                # print('error', e)
        if not quiet:
            if counter:
                print('enter points tma_strategy_find_open_short:', counter)

    def bbands_strategy_find_open_long(self, frame, quiet=False):  # Bollinger bands + MACD
        lim_d = self.params['in_lim_down']
        lim_u = self.params['in_lim_up']
        macd_h = self.indicators.arr[frame]['macd_h']
        bb_l_2 = self.indicators.arr[frame]['bb_l_2']
        bb_u_2 = self.indicators.arr[frame]['bb_u_2']
        bb_m_2 = self.indicators.arr[frame]['bb_m_2']
        charts = self.indicators.data.charts[frame]

        counter = 0
        for i in range(self.total_candles):
            try:
                if macd_h[i - 2] > macd_h[i - 1] and macd_h[i - 1] < macd_h[i]:
                    if percent(bb_l_2[i], bb_u_2[i]) > 0.25:
                        if bb_m_2[i] - bb_l_2[i] != 0:
                            d = (charts[i]['low'] - bb_m_2[i]) / ((bb_m_2[i] - bb_l_2[i]) / 100)
                            # print(arr['utc_date'][i], percent(arr['bb_l_2'][i], arr['bb_u_2'][i]))

                            if bb_m_2[i - 1] > bb_m_2[i]:  # на падающем тренде
                                if d < lim_d:
                                    self.append_point('open', i, 'long')
                                    counter += 1
                            else:  # на растущем тренде
                                if d < lim_u:
                                    self.append_point('open', i, 'long')
                                    counter += 1
            except Exception as e:
                print('error', e)

        if not quiet:
            print('enter points bbands_strategy_find_open_long:', counter)

# def find_enter_rsi(arr, params, no_print=False):     # RSI + MACD
#     if not _points:
#         _points = {'x': [], 'y': [], 'timestamp': [], 'type': [], 'marker': []}
#     lim_d = params['in_lim_down']
#     lim_u = params['in_lim_up']
#     # lim_d = -100
#     # lim_u = 100
#     for i in arr['range']:
#         try:
#             if arr['macd_h'][i-2] > arr['macd_h'][i-1] and arr['macd_h'][i-1] < arr['macd_h'][i]:
#                 if min(arr['rsi'][i-2], arr['rsi'][i-1], arr['rsi'][i]) < 30:
#                     points = append_point(points, arr['charts'], i, 'long')
#         except Exception as e:
#             print('error', e)
#
#     if not no_print:
#         print('enter points:', len(points['x']))
#     return points


# def find_exit_points(arr, params, no_print=False):
#     points = {'x': [], 'y': [], 'unix_time': [], 'marker': []}
#     # lim_down = params['out_lim_down']
#     # lim_up = params['out_lim_up']
#
#     try:
#         for i in range(len(arr['unix_time'])):
#             #   ema на падающем тренде  переход macd через 0
#             if arr['ema_f'][i-1] > arr['ema_s'][i-1]:
#                 if arr['ema_f'][i] < arr['ema_s'][i]:
#                     points = append_point(points, arr['xdate'][i], arr['low'][i], arr['unix_time'][i], 0.1, 0)
#
#             #   на падающем тренде
#             # if arr['ema_fast'][i] < arr['ema_slow'][i]:
#             #     if arr['macd_out_h'][i - 1] > 0 > arr['macd_out_h'][i] and arr['macd_out'][i] > 0:
#             #         # if (arr['low'][i] / arr['ema_slow'][i]) / (arr['ema_fast'][i] / arr['ema_slow'][i]) < params['out_lim_down']:
#             #         points = append_point(points, arr['date'][i], arr['high'][i], arr['unix_time'][i], -0.1, 0)
#
#             #   на растущем тренде
#             # if arr['ema_f'][i] > arr['ema_s'][i]:
#             #     if arr['macd_out_h'][i - 1] > 0 > arr['macd_out_h'][i] and arr['macd_out'][i] > 0:
#             #         # print(arr['date'][i], round((arr['close'][i] / arr['ema_slow'][i]) / (arr['ema_fast'][i] / arr['ema_slow'][i]), 4))
#             #         if (arr['low'][i] - arr['ema_f'][i]) / (arr['close'][i] - arr['ema_s'][i]) > params['out_lim_up']:
#             #             points = append_point(points, arr['xdate'][i], arr['high'][i], arr['unix_time'][i], -0.1, 2)
#
#     except KeyError:
#         pass
#     if not no_print:
#         print('exit points:', len(points['x']))
#     return points


# def find_minimums(arr):
#     points = {'x': [], 'y': [], 'unix_time': [], 'marker': []}
#     try:
#         for i in range(len(arr['low'])):
#             if arr['low'][i] < min([arr['low'][i-_] for _ in range(1, 90)]):
#                 if arr['low'][i] < min([arr['low'][i+_] for _ in range(1, 90)]):
#                     # points = append_point(points, arr['date'][i], arr['low'][i], arr['unix_time'][i], 0, 2)
#                     points = append_point(points, arr['date'][i+1], arr['low'][i+1], arr['unix_time'][i+1], 0, 2)
#                     # points.add(arr['t'][i+1])
#                     # points.add(arr['t'][i+2])
#
#     except IndexError as err:
#         pass
#     print([i for i in points['unix_time']])
#     print('minimums:', len(points['x']))
#     return points

    # def ichimiku_strategy_find_open_long(self, quiet=False):
    #     conversion = self.indicators.arr['ichimoku']['conversion']
    #     base = self.indicators.arr['ichimoku']['base']
    #     senkou_span_a = self.indicators.arr['ichimoku']['senkou_span_a']
    #     senkou_span_b = self.indicators.arr['ichimoku']['senkou_span_b']
    #     lagging = self.indicators.arr['ichimoku']['lagging']
    #     charts = self.indicators.data.charts
    #
    #     counter = 0
    #     for i in range(self.total_candles):
    #         try:
    #             if conversion[i] > base[i]:
    #                 if senkou_span_a[i + 26] > senkou_span_b[i + 26]:  # a > b - green cloud
    #                     if charts[i]['close'] > max(senkou_span_a[i], senkou_span_b[i]) \
    #                             and True in [charts[x]['open'] < max(senkou_span_a[x], senkou_span_b[x]) for x in range(i - 1, i)]:  # свеча выходит из облака вверх
    #                         # if lagging[i - 26] > max(senkou_span_a[i - 26], senkou_span_b[i - 26]):  # lag line выше облака
    #                         self.append_point('open', i, 'long', rate=charts[i]['close'], marker=9)
    #                         counter += 1
    #         except Exception as e:
    #             pass
    #
    #     if not quiet:
    #         print('enter points ichimiku_strategy_find_open_long:', counter)
    #
    # def ichimiku_strategy_find_open_short(self, quiet=False):
    #     conversion = self.indicators.arr['ichimoku']['conversion']
    #     base = self.indicators.arr['ichimoku']['base']
    #     senkou_span_a = self.indicators.arr['ichimoku']['senkou_span_a']
    #     senkou_span_b = self.indicators.arr['ichimoku']['senkou_span_b']
    #     lagging = self.indicators.arr['ichimoku']['lagging']
    #     charts = self.indicators.data.charts
    #
    #     counter = 0
    #     for i in range(self.total_candles):
    #         try:
    #             if conversion[i] < base[i]:
    #                 if senkou_span_a[i + 26] < senkou_span_b[i + 26]:  # a < b - red cloud
    #                     if charts[i]['close'] < min(senkou_span_a[i], senkou_span_b[i]) \
    #                             and True in [charts[x]['open'] > min(senkou_span_a[x], senkou_span_b[x]) for x in range(i - 1, i)]:  # свеча выходит из облака вверх
    #                         if lagging[i - 26] < min(senkou_span_a[i - 26], senkou_span_b[i - 26]):  # lag line ниже облака
    #                             self.append_point('open', i, 'short', rate=charts[i]['close'], marker=10)
    #                             counter += 1
    #         except Exception as e:
    #             pass
    #
    #     if not quiet:
    #         print('enter points ichimiku_strategy_find_open_short:', counter)
