from inc.inc_system import find_candle_start_time, sleep, time, utc_timestamp_to_date
from inc.inc_functions import weighted_average, percent
from config import *


class Charts:
    def __init__(self, pair, api):
        self.pair = pair
        self.api = api
        self.glob = api.glob
        self.log = api.log
        self.data = {i: [] for i in conf_time_frames}
        self.lock = False

        self.cache = {i: {'h': 0, 'l': 0, 'o': 0, 'c': 0, 'v': 0, 'r': [], 'a': []} for i in conf_time_frames}

    def update_by_socket(self, rate, amount):
        while True:
            if not self.lock:
                self.lock = True
                _h = self.data['5m'][-1]['high']
                _l = self.data['5m'][-1]['low']
                if self.data:
                    for frame in conf_time_frames:
                        # перебираем активные таймфреймы
                        now = find_candle_start_time(time(), conf_time_frames[frame])
                        if self.data[frame][-1]['timestamp'] == now:
                            # обновление свечи, если она уже есть
                            # print('обновляю текущую свечу')
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
                        else:
                            # добавление свечи
                            lost_periods = int((time() - self.data[frame][-1]['timestamp']) // conf_time_frames[frame])
                            if lost_periods >= 2:
                                # не было торгов несколько свечей
                                for _ in range(lost_periods - 1):
                                    # все пропущенные, кроме последней
                                    lost_timestamp = self.data[frame][-1]['timestamp'] + conf_time_frames[frame]
                                    self.data[frame].append({
                                        'timestamp': lost_timestamp,
                                        'utc_date': utc_timestamp_to_date(lost_timestamp),
                                        'high': self.data[frame][-1]['close'],
                                        'low': self.data[frame][-1]['close'],
                                        'open': self.data[frame][-1]['close'],
                                        'close': self.data[frame][-1]['close'],
                                        'mean': self.data[frame][-1]['close'],
                                        'volume': 0,
                                        'c_volume': 0,
                                        'amplitude': 0,
                                    })

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
                else:
                    self.log.log(self.pair, 'update_charts_by_socket -> charts не готов')
                self.lock = False
                break

    def update_by_request(self, candles):
        for frame in conf_time_frames:
            self.update_frame(candles, frame)

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
                                    if self.data[frame][y]['timestamp'] == res[x]['timestamp']:
                                        self.data[frame][y] = res[x]
                                        break
                                    if self.data[frame][y - 1]['timestamp'] < res[x]['timestamp'] < self.data[frame][y]['timestamp']:
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

    def check_charts_integrity(self, data, frame):
        for i in range(-1, -len(data), -1):
            if data[i]['timestamp'] - data[i - 1]['timestamp'] != conf_time_frames[frame]:
                self.log.log(self.pair, '---------------------------------------------------------------------')
                self.log.log(self.pair, 'нарушена целостность дат: {}'.format(utc_timestamp_to_date(data[i]['timestamp'])))
                self.log.log(self.pair, 'от: {} {}'.format(data[i - 1]['timestamp'], utc_timestamp_to_date(data[i - 1]['timestamp'])))
                self.log.log(self.pair, 'до: {} {}'.format(data[i]['timestamp'], utc_timestamp_to_date(data[i]['timestamp'])))
                self.log.log(self.pair, 'get.data[{}]: '.format(frame), [i['timestamp'] for i in data[i-2::]])
                self.log.log(self.pair, '---------------------------------------------------------------------')
                self.glob.stop_by['charts'] = True
                return False
        self.glob.stop_by['charts'] = False
        return True

    def check_charts_relevance(self, frame):
        current_candle_time = find_candle_start_time(time(), conf_time_frames[frame])
        if current_candle_time - self.data[frame][-1]['timestamp'] > conf_time_frames[frame]:
            self.log.log(self.pair, '----------------------------------------------------------------------------')
            self.log.log(self.pair, 'frame {} последняя свеча слишком стара: {}'.format(frame, utc_timestamp_to_date(self.data[frame][-1]['timestamp'])))
            self.log.log(self.pair, '----------------------------------------------------------------------------')
            self.glob.stop_by['charts'] = True
            return False
        self.glob.stop_by['charts'] = False
        return True

    def check_charts_relevance_all_frames(self):
        for frame in conf_time_frames:
            if not self.check_charts_relevance(frame):
                self.glob.stop_by['charts'] = True
        self.glob.stop_by['charts'] = False

    def charts_truncate(self):
        for frame in conf_time_frames:
            while True:
                if not self.lock:
                    self.lock = True
                    self.data[frame] = self.data[frame][-conf_total_candles:]
                    self.lock = False
                    break


def get_charts_formatted(res):
    return [{'timestamp': int(i['date']),
             'utc_date': utc_timestamp_to_date(i['date']),
             'high': float(i['high']),
             'low': float(i['low']),
             'open': float(i['open']),
             'close': float(i['close']),
             'mean': float(i['weightedAverage']),
             'volume': float(i['volume']),
             'c_volume': float(i['quoteVolume']),
             'amplitude': round(percent(float(i['low']), float(i['high'])), 2)
             } for i in res]
