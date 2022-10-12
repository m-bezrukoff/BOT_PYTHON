from simulator_v2.playground_enter_points import *
from inc.inc_system import *
import os


class Data:
    def __init__(self, parameters):
        self.pair = parameters['pair']
        self.frame = parameters['frame']
        self.params = parameters
        self.cache = {x: {} for x in self.params['time_frames']}

        self.from_timestamp = utc_date_to_timestamp(parameters['from'])
        self.to_timestamp = utc_date_to_timestamp(parameters['to'])

        # self.indicators_margin = int(2.8 * max([parameters[_] for _ in parameters if type(parameters[_]) == int and 'opt_' not in _]) + self.offset)
        # self.from_margined = {x: self.from_timestamp - (self.indicators_margin * self.params['time_frames'][x]) for x in self.params['time_frames']}
        # self.new_candles_count = {x: 0 for x in self.params['time_frames']}     # 0 - нет новой свечи, 1,2,3.. - кол-во новых свечей
        # self.window = {x: (self.to_timestamp - self.from_timestamp) // self.params['time_frames'][x] for x in self.params['time_frames']}
        # self.offset = 10  # добавляемое кол-во свечей для корректной работы на начальных итерациях (например tma_f[-3])
        # self.tradebook = self.load_tradebook_cache()
        # self.charts = self.load_charts_cache()
        # self.populate_charts_from_tradebook()

        self.margin = int
        self.tradebook = []
        self.charts = []
        self.tradebook_charts_loader()
        self.total_trades = len(self.tradebook)
        self.charts_export = {x: [] for x in self.params['time_frames']}  # timeframes завершенных свечей для передачи в коллектор
        self.added_candles = {x: 0 for x in self.params['time_frames']}   # кол-во всех добавленных свечей

    #     self.trades = []
    #     self.trade_balance = 0
    #     self.trade_speed = 0
    #     self.last_rate = 0
    #
    # def trade_stats(self, date, rate, amount, typ):
    #     # print(date, rate, amount, typ)
    #     self.trades.append({'date': date, 'type': typ})
    #     self.trades = [i for i in self.trades if i['date'] > date - 300]
    #     self.trade_speed = len(self.trades)
    #     try:
    #         self.trade_balance = int(len([i for i in self.trades if i['type'] == 'buy']) / self.trade_speed * 100)
    #     except ZeroDivisionError:
    #         self.trade_balance = 0
    #
    #     fr = utc_date_to_timestamp('2021-01-05 00:45:00')
    #     to = utc_date_to_timestamp('2021-01-05 01:15:00')
    #     if to > date > fr:
    #         print('{} speed: {}  buys: {} %     rate {} %'.format(utc_timestamp_to_date(date), self.trade_speed, self.trade_balance, to2(percent(self.last_rate, rate))))
    #
    #     self.last_rate = rate
    def tradebook_charts_loader(self):
        _hash = md5_hash(self.pair + str(self.from_timestamp) + str(self.to_timestamp) + str(self.params))
        cache_file = 'save/_cache_' + self.pair + '_' + _hash + '.dat'
        # cache_data = {'charts': {x: [] for x in self.params['time_frames']}, 'tradebook': [], 'margin': int}
        if os.path.isfile(cache_file):
            cached_data = load_zipped_pickle(cache_file)
            self.tradebook = cached_data['tradebook']
            self.charts = cached_data['charts']
            self.margin = cached_data['margin']
            print('tradebook and charts loaded from cache')
        else:
            file_tradebook = 'save/' + self.pair + '_tradebook.dat'
            tradebook = load_zipped_pickle(file_tradebook)
            # res = [trade for trade in load_zipped_pickle(file) if self.to_timestamp > trade['date'] >= self.from_timestamp]


    def load_tradebook_cache(self):
        cache_file = 'save/_cache_tradebook_' + self.pair + '_' + str(self.from_timestamp) + '_' + str(self.to_timestamp) + '.dat'
        if os.path.isfile(cache_file):
            return load_zipped_pickle(cache_file)
        file = 'save/' + self.pair + '_tradebook.dat'
        res = [trade for trade in load_zipped_pickle(file) if self.to_timestamp > trade['date'] >= self.from_timestamp]
        save_zipped_pickle(cache_file, res)
        return res

    def load_charts_cache(self):
        self.from_margined = {x: self.from_timestamp - (self.indicators_margin * self.params['time_frames'][x]) for x in self.params['time_frames']}
        cache_file = 'save/_cache_charts_' + self.pair + '_' + str(self.from_timestamp) + '_' + str(self.to_timestamp) + '_' + str(self.indicators_margin) + '.dat'
        charts_file = 'save/' + self.pair + '_charts.dat'
        if os.path.isfile(cache_file):
            return load_zipped_pickle(cache_file)
        # if os.path.isfile(charts_file):
        #     temp = load_zipped_pickle(charts_file)
        #     res = {x: [] for x in self.params['time_frames']}
        #     for frame in self.params['time_frames']:
        #         res[frame] = [chart for chart in temp[frame] if self.to_timestamp > chart['timestamp'] >= self.from_margined[frame]]
        #     save_zipped_pickle(cache_file, res)
        #     return res

        return {x: [] for x in self.params['time_frames']}

    def populate_charts_from_tradebook(self):
        t1 = time()
        for i in self.tradebook:
            self.update_charts(i['date'], i['rate'], i['amount'], i['type'])
        print('charts population took', to2(time() - t1), 'sec')

    def update_charts(self, date, rate, amount, typ):
        for frame in self.params['time_frames']:  # перебираем активные таймфреймы
            # print('---', self.charts[frame][-1]['timestamp'], date)
            now = find_candle_start_time(date, frame)
            if self.charts[frame]:
                if date < self.charts[frame][-1]['timestamp']:
                    raise Exception('WRONG TRADE TIME')

                if self.charts[frame][-1]['timestamp'] == now:  # обновление свечи, если она уже есть
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

                    self.charts[frame][-1] = {
                        'timestamp': now,
                        'utc_date': utc_timestamp_to_date(now),
                        'high': self.cache[frame]['h'],
                        'low': self.cache[frame]['l'],
                        'open': self.cache[frame]['o'],
                        'close': self.cache[frame]['c'],
                        # 'mean': weighted_average(self.cache[frame]['r'], self.cache[frame]['a']),
                        # 'volume': self.cache[frame]['v'] * rate,
                        # 'c_volume': self.cache[frame]['v'],
                        'amplitude': round(percent(self.cache[frame]['l'], self.cache[frame]['h']), 2),
                    }

                else:  # добавление свечи
                    lost_periods = (date - self.charts[frame][-1]['timestamp']) // self.params['time_frames'][frame]
                    if lost_periods >= 2:
                        # self.new_candles_count[frame] = lost_periods
                        # если не было торгов несколько свечей
                        # self.new_candles_count[frame] = True
                        for _ in range(lost_periods - 1):
                            lost_timestamp = self.charts[frame][-1]['timestamp'] + self.params['time_frames'][frame]

                            self.charts[frame].append({
                                'timestamp': lost_timestamp,
                                'utc_date': utc_timestamp_to_date(lost_timestamp),
                                'high': self.charts[frame][-1]['close'],
                                'low': self.charts[frame][-1]['close'],
                                'open': self.charts[frame][-1]['close'],
                                'close': self.charts[frame][-1]['close'],
                                'amplitude': 0,
                            })

                            self.added_candles[frame] += 1
                            if self.added_candles[frame] > 1:
                                self.charts_export[frame].append(self.charts[frame][-2]['timestamp'])

                    self.cache[frame]['r'] = [rate]
                    self.cache[frame]['a'] = [amount]
                    self.cache[frame]['o'] = self.cache[frame]['c'] = self.cache[frame]['h'] = self.cache[frame]['l'] = rate
                    self.cache[frame]['v'] = amount

                    self.charts[frame].append({
                        'timestamp': now,
                        'utc_date': utc_timestamp_to_date(now),
                        'high': rate,
                        'low': rate,
                        'open': rate,
                        'close': rate,
                        # 'mean': rate,
                        # 'volume': amount * rate,
                        # 'c_volume': amount,
                        'amplitude': 0,
                    })

                    self.added_candles[frame] += 1
                    if self.added_candles[frame] > 1:
                        self.charts_export[frame].append(self.charts[frame][-2]['timestamp'])
