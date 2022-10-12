from simulator_v3.playground_enter_points import *
import numpy as np
import os
from inc.inc_system import *


class Data:
    def __init__(self, parameters):
        self.params = parameters
        self.pair = parameters['pair']
        self.frame = parameters['frame']
        self.from_timestamp = utc_date_to_timestamp(parameters['from'])
        self.to_timestamp = utc_date_to_timestamp(parameters['to'])

        self.time_update_charts = 0
        self.time_update_indicators = 0
        self.margin = 300       # отсуп свечей для рассчета индикаторов
        self.time_margin = {x: self.from_timestamp - self.margin * self.params['time_frames'][x] for x in self.params['time_frames']}   # отступ секунд для рассчета индикаторов

        self.cache = {x: {} for x in self.params['time_frames']}
        self.added_candles = {x: 0 for x in self.params['time_frames']}   # кол-во всех добавленных свечей за один трейд
        self.timestamp = 0
        # self.tradebook_limiter = 0 if not tradebook else limiter  # граница отступа от перебираемого диапазона
        self.tradebook_limiter = 0

        self.charts = {frame: {
            'o': np.array([], dtype='float64'),
            'c': np.array([], dtype='float64'),
            'h': np.array([], dtype='float64'),
            'l': np.array([], dtype='float64'),
            'ha_o': np.array([], dtype='float64'),
            'ha_c': np.array([], dtype='float64'),
            'ha_h': np.array([], dtype='float64'),
            'ha_l': np.array([], dtype='float64'),
            'volume': np.array([], dtype='float64'),
            # 'amplitude_average': [],    # средняя амплитуда за последние 10 свечей
            'amplitude': np.array([], dtype='float64'),
            'timestamp': np.array([], dtype='int64'),
            'utc_date': np.array([]),
        } for frame in self.params['time_frames']}

        self.tradebook = self.tradebook_loader()
        self.total_trades = len(self.tradebook)
        self.initial_charts()

    def tradebook_loader(self):
        _hash = md5_hash(self.pair + str(self.from_timestamp) + str(self.to_timestamp) + str(self.params['time_frames']))
        cache_tradebook_file = 'save/_cache_' + self.pair + '_' + _hash + '.dat'
        if os.path.isfile(cache_tradebook_file):
            tradebook = load_zipped_pickle(cache_tradebook_file)
        else:
            tradebook_file = 'save/' + self.pair + '_tradebook.dat'
            tradebook = load_zipped_pickle(tradebook_file)
            margined_from = self.from_timestamp - max(self.params['time_frames'].values()) * self.margin
            # загружаем всегда с большим отступом слева, для гаранатированного расчета ema с большим периодом
            tradebook = [i for i in tradebook if self.to_timestamp > i['date'] >= margined_from]
            save_zipped_pickle(cache_tradebook_file, tradebook)
        return tradebook

    def initial_charts(self):
        for trade in self.tradebook:
            if trade['date'] < self.from_timestamp:
                # print(trade['date'])
                self.tradebook_limiter += 1
                self.update_charts(trade['date'], trade['rate'], trade['amount'], trade['type'])
            else:
                break

    def charts_add_candle(self, frame, o, c, h, l, v, utc, timestamp, typ):
        self.charts[frame]['o'] = np.append(self.charts[frame]['o'], o)
        self.charts[frame]['c'] = np.append(self.charts[frame]['c'], c)
        self.charts[frame]['h'] = np.append(self.charts[frame]['h'], h)
        self.charts[frame]['l'] = np.append(self.charts[frame]['l'], l)
        self.charts[frame]['volume'] = np.append(self.charts[frame]['volume'], v)
        self.charts[frame]['utc_date'] = np.append(self.charts[frame]['utc_date'], utc_timestamp_to_date(utc))
        self.charts[frame]['timestamp'] = np.append(self.charts[frame]['timestamp'], timestamp)
        self.charts[frame]['amplitude'] = np.append(self.charts[frame]['amplitude'], 0)
        # self.charts[frame]['amplitude_average'] = 0

        # Heiken Ashi
        try:
            self.charts[frame]['ha_o'] = np.append(self.charts[frame]['ha_o'], (self.charts[frame]['ha_o'][-1] + self.charts[frame]['ha_c'][-1]) / 2)
        except IndexError:
            self.charts[frame]['ha_o'] = np.append(self.charts[frame]['ha_o'], (o + c) / 2)

        self.charts[frame]['ha_c'] = np.append(self.charts[frame]['ha_c'], (o + c + h + l) / 4)
        self.charts[frame]['ha_h'] = np.append(self.charts[frame]['ha_h'], h)
        self.charts[frame]['ha_l'] = np.append(self.charts[frame]['ha_l'], l)

    def charts_update_candle(self, frame, v, typ):
        self.charts[frame]['c'][-1] = self.cache[frame]['c']
        self.charts[frame]['h'][-1] = self.cache[frame]['h']
        self.charts[frame]['l'][-1] = self.cache[frame]['l']
        self.charts[frame]['volume'][-1] = self.charts[frame]['volume'][-1] + v
        self.charts[frame]['amplitude'][-1] = round(percent(self.cache[frame]['l'], self.cache[frame]['h']), 2)
        # self.charts[frame]['amplitude_average'] = mean([self.charts[frame]['amplitude'][i] for i in range(-1, -11, -1)])

        # Heiken Ashi
        self.charts[frame]['ha_c'][-1] = (self.charts[frame]['o'][-1] + self.charts[frame]['h'][-1] + self.charts[frame]['l'][-1] + self.charts[frame]['c'][-1]) / 4
        self.charts[frame]['ha_h'][-1] = max(self.charts[frame]['ha_o'][-1], self.charts[frame]['ha_c'][-1], self.charts[frame]['h'][-1])
        self.charts[frame]['ha_l'][-1] = min(self.charts[frame]['ha_o'][-1], self.charts[frame]['ha_c'][-1], self.charts[frame]['l'][-1])

    def update_charts(self, date, rate, amount, typ):
        self.timestamp = date

        for frame in self.params['time_frames']:  # перебираем активные таймфреймы
            # print('---', self.charts[frame][-1]['timestamp'], date)
            if date > self.time_margin[frame]:  # отступ каждого фрейма для индикаторов
                now = find_candle_start_time(date, self.params['time_frames'][frame])
                self.added_candles[frame] = 0
                if len(self.charts[frame]['timestamp']) > 0:
                    if date < self.charts[frame]['timestamp'][-1]:
                        print(date, utc_timestamp_to_date(self.charts[frame]['timestamp'][-1]))
                        raise Exception('WRONG TRADE TIME', date, utc_timestamp_to_date(date))

                    if self.charts[frame]['timestamp'][-1] == now:  # обновление свечи, если она уже есть
                        if not self.cache[frame]['o']:
                            self.cache[frame]['o'] = self.cache[frame]['c'] = self.cache[frame]['h'] = self.cache[frame]['l'] = rate
                        if rate > self.cache[frame]['h']:
                            self.cache[frame]['h'] = rate
                        if rate < self.cache[frame]['l']:
                            self.cache[frame]['l'] = rate
                        self.cache[frame]['c'] = rate
                        self.cache[frame]['volume'] += amount

                        self.charts_update_candle(frame, amount, typ)
                        continue

                    else:  # добавление свечи
                        lost_periods = (date - self.charts[frame]['timestamp'][-1]) // self.params['time_frames'][frame]
                        if lost_periods >= 2:
                            '''
                            self.new_candles_count[frame] = lost_periods, если не было торгов несколько свечей self.new_candles_count[frame] = True
                            '''
                            for _ in range(lost_periods - 1):
                                lost_timestamp = self.charts[frame]['timestamp'][-1] + self.params['time_frames'][frame]
                                lost_rate = self.charts[frame]['c'][-1]
                                self.charts_add_candle(frame, lost_rate, lost_rate, lost_rate, lost_rate, 0, lost_timestamp, lost_timestamp, 0)
                                self.added_candles[frame] += 1

                self.cache[frame]['r'] = [rate]
                self.cache[frame]['a'] = [amount]
                self.cache[frame]['o'] = self.cache[frame]['c'] = self.cache[frame]['h'] = self.cache[frame]['l'] = rate
                self.cache[frame]['volume'] = amount
                self.charts_add_candle(frame, rate, rate, rate, rate, amount * rate, now, now, typ)
                self.added_candles[frame] += 1
