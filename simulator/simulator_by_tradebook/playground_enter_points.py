from inc.inc_functions import percent, add_percent, weighted_average
from inc.inc_system import to2, to8
from statistics import mean


class Job:
    def __init__(self, indicators):
        self.indicators = indicators
        self.params = indicators.data.params
        self.data = indicators.data
        self.charts = indicators.data.charts

        self.total_candles = 0
        self.points = {frame: {'open': {}, 'close': {}} for frame in self.params['time_frames']}
        self.rate = 0
        self.timestamp = 0

        self.margin = self.data.indicators_margin - self.data.offset

    def run(self, timestamp):
        self.timestamp = timestamp
        frame = self.params['frame']
        self.rate = self.charts[frame][-1]['close']
        self.total_candles = len(self.indicators.timestamps)

        # self.find_open_long_fractals(frame)
        self.find_open_long_jma_cross(frame)
        self.find_close_long_jma_cross(frame)
        # self.find_open_long_bb(frame)
        # self.find_close_long_bb(frame)
        # self.find_close_long_tma_cross(frame)
        # self.find_open_long_tma_cross(frame)

        # self.find_open_long_tma(frame)
        # self.find_close_long_tma(frame)
        # self.tma_strategy_find_open_short('frame)
        # self.tma_strategy_find_close_long('frame)

    def find_open_long_jma_cross(self, frame):
        ema_f = self.indicators.arr[frame]['ema_f'][self.margin:]
        ema_m = self.indicators.arr[frame]['ema_m'][self.margin:]

        if ema_f[-2] < ema_m[-2] and ema_f[-1] > ema_m[-1]:
            stoploss = min([i['low'] for i in self.charts[frame][-3:]])
            self.append_point_by_tradebook(frame, 'open', 'long', self.rate, stoploss, marker=9)

    def find_close_long_jma_cross(self, frame):
        ema_f = self.indicators.arr[frame]['ema_f'][self.margin:]
        ema_m = self.indicators.arr[frame]['ema_m'][self.margin:]

        if ema_f[-2] > ema_m[-2] and ema_f[-1] < ema_m[-1]:
            stoploss = min([i['low'] for i in self.charts[frame][-3:]])
            self.append_point_by_tradebook(frame, 'close', 'long', self.rate, stoploss, marker=11)

    def find_open_long_bb(self, frame):
        bb_u_2 = self.indicators.arr[frame]['bb_u_2'][self.margin:]
        bb_m_2 = self.indicators.arr[frame]['bb_m_2'][self.margin:]
        bb_l_2 = self.indicators.arr[frame]['bb_l_2'][self.margin:]
        ema_f = self.indicators.arr[frame]['ema_f'][self.margin:]
        ema_m = self.indicators.arr[frame]['ema_m'][self.margin:]
        ema_s = self.indicators.arr[frame]['ema_s'][self.margin:]
        ema_xs = self.indicators.arr[frame]['ema_xs'][self.margin:]
        stoch_rsi_d = self.indicators.arr[frame]['stoch_rsi_d'][self.margin:]
        stoch_rsi_k = self.indicators.arr[frame]['stoch_rsi_k'][self.margin:]

        charts = self.charts[frame][self.margin:]

        if ema_f[-2] < ema_m[-2] and ema_f[-1] > ema_m[-1]:

        # if stoch_rsi_k[-2] < 1:
        #     if stoch_rsi_d[-1] < stoch_rsi_k[-1]:
        #         if self.rate < bb_m_2[-1] - 0.7 * (bb_m_2[-1] - bb_l_2[-1]):  # только просадка на Х ниже BB middle
        #         if ema_xs[-1] < ema_s[-1]:  # только на росте
        #
        #                 # print(stoch_rsi_d[-1], stoch_rsi_k[-1])
        #             stoploss = ema_s[-1]
        #             stoploss = min([i['low'] for i in self.charts[frame][-3:]])
            stoploss = bb_l_2[-1] - 0.2 * (bb_m_2[-1] - bb_l_2[-1])
            self.append_point_by_tradebook(frame, 'open', 'long', self.rate, stoploss, marker=9)

        # if charts[-2]['low'] < bb_l_2[-2]:
        #     if charts[-2]['close'] <= charts[-1]['open']:
        #         if charts[-2]['close'] <= charts[-1]['open']:
        #             if self.rate > bb_l_2[-1]:
                        # if self.rate < mean([bb_l_2[-1], bb_l_2[-1], bb_m_2[-1]]):
                        # if stoch_rsi_d[-2] > stoch_rsi_k[-2] and stoch_rsi_d[-1] < stoch_rsi_k[-1]:
                            # if self.rate < ema[-1]:
                        # if tma_f[-3] > tma_f[-2] < tma_f[-1]:
                        # stoploss = min([i['low'] for i in self.charts[frame][-3:]])
                        # stoploss = add_percent(self.rate, -0.4)
                        # self.append_point_by_tradebook(frame, 'open', 'long', charts[-1]['close'], stoploss, marker=9)
        # if stoch_rsi_d[-2] <= 2 and stoch_rsi_k[-2] <= 2:
        # if ema[-2] < ema[-1]:

        # if tma_f_ema[-2] < tma_m_ema[-2] and tma_f_ema[-1] > tma_m_ema[-1]:
        # if ema_dif_ema[-3] > ema_dif_ema[-2] and ema_dif_ema[-2] < ema_dif_ema[-1]:
        # if stoch_rsi_d[-2] > stoch_rsi_k[-2] and stoch_rsi_d[-1] < stoch_rsi_k[-1]:   # +- можно пробовать
            # if (self.rate - bb_l_2[-1]) * 100 / (bb_m_2[-1] - bb_l_2[-1]) < 10:
        # if ema_dif_ema[-2] < 0 < ema_dif_ema[-1]:
            # if self.rate < mean([bb_l_2[-1], bb_l_2[-1], bb_m_2[-1]]):

        # if charts[-2]['close'] < bb_l_2[-2]:
        #     if self.rate > bb_l_2[-1]:
                # if atr[-2] > atr[-1] and atr[-3] > atr[-2]:
                    # if charts[-2]['low'] >= charts[-3]['low'] and charts[-2]['close'] > charts[-2]['open']:
                    # if (bb_u_2[-1] - bb_l_2[-1]) / atr[-1] > 3:
                        # print((bb_u_2[-1] - bb_l_2[-1]) / atr[-1])
                # stoploss = min([i['low'] for i in self.charts[frame][-3:]])
                # # stoploss = add_percent(self.rate, -0.3)
                # self.append_point_by_tradebook(frame, 'open', 'long', charts[-1]['close'], stoploss, marker=9)










    def find_close_long_bb(self, frame):
        stoch_rsi_d = self.indicators.arr[frame]['stoch_rsi_d'][self.margin:]
        stoch_rsi_k = self.indicators.arr[frame]['stoch_rsi_k'][self.margin:]
        charts = self.charts[frame][self.margin:]

        if stoch_rsi_d[-2] >= 98 and stoch_rsi_k[-2] >= 98:
            if stoch_rsi_d[-1] < 100 and stoch_rsi_d[-1] > stoch_rsi_k[-1]:
                # if self.rate < charts[-2]['close']:
                self.append_point_by_tradebook(frame, 'close', 'long', self.rate, marker=11)







    def find_open_long_tma_cross(self, frame):
        bb_m_2 = self.indicators.arr[frame]['bb_m_2'][self.margin:]
        tma_f = self.indicators.arr[frame]['tma_f'][self.margin:]
        tma_m = self.indicators.arr[frame]['tma_m'][self.margin:]
        charts = self.charts[frame][self.margin:]
        if tma_f[-2] < tma_m[-2] and tma_f[-1] > tma_m[-1]:
            stoploss = min([i['low'] for i in self.charts[frame][-5:]])
            self.append_point_by_tradebook(frame, 'open', 'long', charts[-1]['close'], stoploss, marker=9)

    def find_close_long_tma_cross(self, frame):
        bb_m_2 = self.indicators.arr[frame]['bb_m_2'][self.margin:]
        tma_f = self.indicators.arr[frame]['tma_f'][self.margin:]
        tma_m = self.indicators.arr[frame]['tma_m'][self.margin:]
        ema_dif = self.indicators.arr[frame]['ema_dif'][self.margin:]
        charts = self.charts[frame][self.margin:]
        if self.rate > bb_m_2[-1] and self.rate > tma_m[-1]:
            if ema_dif[-3] < ema_dif[-2]:
                if percent(ema_dif[-2], ema_dif[-1]) < -5:
                    self.append_point_by_tradebook(frame, 'close', 'long', charts[-1]['close'], marker=11)

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

    def append_point_by_tradebook(self, frame, action, typ, rate, stoploss=None, marker=8):
        timestamp = self.charts[frame][-1]['timestamp']
        if not self.points[frame][action].get(timestamp):
            self.points[frame][action][timestamp] = {
                'x': self.charts[frame][-1]['utc_date'],
                'y': rate,
                'type': typ,
                'marker': marker,
                'trade_timestamp': self.timestamp,
                'candle_timestamp': timestamp,
                'stoploss': stoploss
            }
