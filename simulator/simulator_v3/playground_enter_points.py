from inc.inc_functions import percent, add_percent, weighted_average
from inc.inc_system import to2, to8, to6
from statistics import mean
import numpy as np


class Job:
    def __init__(self, indicators):
        self.params = indicators.params
        self.data = indicators.data
        self.charts = indicators.data.charts
        self.indicators = indicators

        self.total_candles = 0
        self.points = {frame: {'open': {}, 'close': {}} for frame in self.params['time_frames']}
        self.points_cache = {i: {'long': [], 'short': []} for i in ['open', 'close']}
        self.rate = 0
        self.margin = {frame: int((self.data.from_timestamp - self.data.to_timestamp) // self.params['time_frames'][frame]) for frame in self.params['time_frames']}

    def run(self):
        frame = self.params['frame']
        self.rate = self.charts[frame]['c'][-1]
        self.total_candles = len(self.indicators.timestamps)
        self.open_long(frame)
        self.close_long(frame)

    def open_long(self, frame):
        # ema_s_speed = self.indicators.arr[frame]['ema_s_speed']
        ema_s = self.indicators.arr[frame]['ema_s']
        ema_m = self.indicators.arr[frame]['ema_m']
        ema_f = self.indicators.arr[frame]['ema_f']
        # ema_band_u = self.indicators.arr[frame]['bb_u_2']
        # ema_band_l = self.indicators.arr[frame]['bb_l_2']
        # stoch_s = self.indicators.arr[frame]['stoch_s']
        # stoch_f = self.indicators.arr[frame]['stoch_f']

        # max_peaks = self.indicators.arr[frame]['points_max_peaks']
        last_min = min(self.charts[frame]['l'][-4:])
        if all([True if self.charts[frame]['ha_o'][i] == self.charts[frame]['ha_h'][i] else False for i in range(-2, -6, -1)]) \
                and self.charts[frame]['ha_o'][-1] != self.charts[frame]['ha_h'][-1] \
                and self.rate > self.charts[frame]['ha_o'][-1] \
                and self.rate > ema_s[-1]:

            # stoploss = add_percent(last_min, -0.05)
            stoploss = add_percent(self.rate, -0.4)
            self.append_point_by_tradebook(frame, 'open', 'long', self.rate, stoploss, marker=0)

    def close_long(self, frame):
        ema_f = self.indicators.arr[frame]['ema_f']
        ema_m = self.indicators.arr[frame]['ema_m']
        # ema_band_u = self.indicators.arr[frame]['bb_u_2']
        # ema_band_l = self.indicators.arr[frame]['bb_l_2']
        # stoch_s = self.indicators.arr[frame]['stoch_s']
        # if ema_f[-2] > ema_band_l[-2] and ema_f[-1] < ema_band_l[-1]:
        if ema_f[-2] > ema_m[-2] and ema_f[-1] < ema_m[-1]:

            self.append_point_by_tradebook(frame, 'close', 'long', self.rate, 0, marker=1)
            # print(
            #     self.charts[frame]['utc_date'][-1],
            #     # self.charts[frame]['timestamp'][-1],
            #     self.data.timestamp,
            #     'stoch_s:', to2(stoch_s[-1]),
            #     # 'stoch_f:', to2(stoch_f[-1]),
            #     # 'stoch_rsi_d:', to2(stoch_rsi_d[-1]),
            #     # 'stoch_rsi_k:', to2(stoch_rsi_k[-1]),
            # )

    def last_peak_to_rate_diff(self, frame):
        h = self.charts[frame]['h']
        for i in range(-1, -len(h), -1):
            if (h[i-4] <= h[i-3] >= h[i-2]) and (h[i-5] <= h[i-3] >= h[i-1]):
                return percent(h[i-2], self.rate)
        return False

    def append_point_by_tradebook(self, frame, action, typ, rate, stoploss=None, marker=8):
        # self.points_cache
        candle_timestamp = self.charts[frame]['timestamp'][-1]
        timestamp = self.data.timestamp
        if candle_timestamp not in self.points_cache[action][typ]:
            self.points[frame][action][timestamp] = {
                'x': self.charts[frame]['utc_date'][-1],
                'y': rate,
                'type': typ,
                'marker': marker,
                'trade_timestamp': self.data.timestamp,
                'candle_timestamp': candle_timestamp,
                'stoploss': stoploss
            }
            self.points_cache[action][typ].append(candle_timestamp)
