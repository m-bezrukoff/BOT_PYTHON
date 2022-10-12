from playground_grid import *
import numpy as np
import os
from inc.inc_system import *
from classes.cls_file_io import FileIO


class Data:
    def __init__(self, parameters):
        self.io = FileIO()
        self.params = parameters
        self.pair = parameters['pair']
        self.from_timestamp = utc_date_to_timestamp(parameters['from'])
        self.to_timestamp = utc_date_to_timestamp(parameters['to'])
        self.file_path = 'save'
        self.time_update_charts = 0
        self.time_update_indicators = 0
        self.margin_candles = 300
        self.time_margin = {frame: self.from_timestamp - self.margin_candles * self.params['time_frames'][frame] for frame in self.params['time_frames']}
        self.cache = {x: {} for x in self.params['time_frames']}
        self.added_candles = {x: 0 for x in self.params['time_frames']}   # кол-во всех добавленных свечей за один трейд
        self.prev_trade = ()

        self.frame_size_min = min(parameters['time_frames'].values())
        self.frame = list(parameters['time_frames'].keys())[list(parameters['time_frames'].values()).index(self.frame_size_min)]

        self.tradebook = self.tradebook_loader()
        self.charts = self.charts_loader()

        self.total_trades = len(self.tradebook)

    def charts_loader(self):
        _hash = md5_hash(self.pair + str(self.from_timestamp) + str(self.to_timestamp) + str(self.params['time_frames']))
        _cache_file = self.file_path + '/charts_' + self.pair + '_' + _hash + '.dat'
        if os.path.isfile(_cache_file):
            _charts = self.io.load_zipped_file(_cache_file)
        else:
            _charts = self.charts = {frame: {
                'o': np.array([], dtype='float64'),
                'c': np.array([], dtype='float64'),
                'h': np.array([], dtype='float64'),
                'l': np.array([], dtype='float64'),
                'volume': np.array([], dtype='float64'),
                'amplitude': np.array([], dtype='float64'),
                'timestamp': np.array([], dtype='int64'),
                'utc_date': np.array([]),
            } for frame in self.params['time_frames']}
            self.render_charts(_cache_file)
        return _charts

    def tradebook_loader(self):
        _hash = md5_hash(self.pair + str(self.from_timestamp) + str(self.to_timestamp) + str(self.params['time_frames']))
        cache_tradebook_file = self.file_path + '/tradebook_' + self.pair + '_' + _hash + '.dat'
        if os.path.isfile(cache_tradebook_file):
            tradebook = self.io.load_zipped_file(cache_tradebook_file)

        else:
            tradebook_file = '../save/' + self.pair + '_tradebook.dat'
            tradebook = self.io.load_zipped_file(tradebook_file)
            margined_from = self.from_timestamp - max(self.params['time_frames'].values()) * self.margin_candles
            # загружаем всегда с большим отступом слева, для гаранатированного расчета ema с большим периодом
            tradebook = [i for i in tradebook if self.to_timestamp > i['date'] >= margined_from]
            if self.check_sequence(tradebook):
                self.io.save_zipped_file(cache_tradebook_file, tradebook)
                print('Tradebook generated, cache file saved')
        return tradebook

    def check_sequence(self, _tradebook):
        for i in range(1, len(_tradebook)):
            if _tradebook[i]['date'] < _tradebook[i - 1]['date'] or _tradebook[i]['id'] - _tradebook[i - 1]['id'] != 1:
                print('Tradebook sequence ERROR', _tradebook[i]['date'], _tradebook[i]['id'], _tradebook[i - 1]['date'], _tradebook[i - 1]['id'])
                return False
        print('Tradebook sequence is OK')
        return True

    def render_charts(self, _cache_file):
        for trade in self.tradebook:
            self.update_charts(trade)
        self.io.save_zipped_file(_cache_file, self.charts)
        print('Charts generated, cache file saved')

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
        # try:
        #     self.charts[frame]['ha_o'] = np.append(self.charts[frame]['ha_o'], (self.charts[frame]['ha_o'][-1] + self.charts[frame]['ha_c'][-1]) / 2)
        # except IndexError:
        #     self.charts[frame]['ha_o'] = np.append(self.charts[frame]['ha_o'], (o + c) / 2)
        #
        # self.charts[frame]['ha_c'] = np.append(self.charts[frame]['ha_c'], (o + c + h + l) / 4)
        # self.charts[frame]['ha_h'] = np.append(self.charts[frame]['ha_h'], h)
        # self.charts[frame]['ha_l'] = np.append(self.charts[frame]['ha_l'], l)

    def charts_update_candle(self, frame, v, typ):
        self.charts[frame]['c'][-1] = self.cache[frame]['c']
        self.charts[frame]['h'][-1] = self.cache[frame]['h']
        self.charts[frame]['l'][-1] = self.cache[frame]['l']
        self.charts[frame]['volume'][-1] = self.charts[frame]['volume'][-1] + v
        self.charts[frame]['amplitude'][-1] = round(percent(self.cache[frame]['l'], self.cache[frame]['h']), 2)
        # self.charts[frame]['amplitude_average'] = mean([self.charts[frame]['amplitude'][i] for i in range(-1, -11, -1)])

        # Heiken Ashi
        # self.charts[frame]['ha_c'][-1] = (self.charts[frame]['o'][-1] + self.charts[frame]['h'][-1] + self.charts[frame]['l'][-1] + self.charts[frame]['c'][-1]) / 4
        # self.charts[frame]['ha_h'][-1] = max(self.charts[frame]['ha_o'][-1], self.charts[frame]['ha_c'][-1], self.charts[frame]['h'][-1])
        # self.charts[frame]['ha_l'][-1] = min(self.charts[frame]['ha_o'][-1], self.charts[frame]['ha_c'][-1], self.charts[frame]['l'][-1])

    def update_charts(self, trade):
        date = trade['date']
        rate = trade['rate']
        amount = trade['amount']
        typ = trade['type']

        for frame in self.params['time_frames']:  # перебираем активные таймфреймы
            # print('---', self.charts[frame][-1]['timestamp'], date)
            if date > self.time_margin[frame]:  # отступ каждого фрейма для индикаторов
                now = find_candle_start_time(date, self.params['time_frames'][frame])
                self.added_candles[frame] = 0
                if len(self.charts[frame]['timestamp']) > 0:
                    if date < self.charts[frame]['timestamp'][-1]:
                        print(self.charts[frame]['timestamp'])
                        print(f'new: {date} {utc_timestamp_to_date(date)} old: {utc_timestamp_to_date(self.charts[frame]["timestamp"][-1])}')
                        print('last trade', self.prev_trade)
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

                self.prev_trade = (date, rate, amount, typ)

                self.cache[frame]['r'] = [rate]
                self.cache[frame]['a'] = [amount]
                self.cache[frame]['o'] = self.cache[frame]['c'] = self.cache[frame]['h'] = self.cache[frame]['l'] = rate
                self.cache[frame]['volume'] = amount
                self.charts_add_candle(frame, rate, rate, rate, rate, amount * rate, now, now, typ)
                self.added_candles[frame] += 1
