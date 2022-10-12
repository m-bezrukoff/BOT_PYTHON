from inc.inc_system import find_first_candle_time, utc_date_to_timestamp, time, utc_timestamp_to_date, find_candle_start_time
from inc.inc_functions import percent_of_sum
from config import *
from classes.cls_dataclasses import PublicTradeData


class Clusters:
    def __init__(self, pair, public_trades):
        self.pair = pair
        self.public_trades = public_trades
        self.log = public_trades.log
        self.data = public_trades.data
        self.data_start_time = update_data_start_time()
        self.clusters = {i: [] for i in conf_time_frames}   # трейды кластеризованные по времени
        self.is_updated = False
        self.lock_data = False
        self.lock_clusters = False

        self.rate_min = 0
        self.rate_max = 0
        self.rate_step = {i: 0 for i in conf_time_frames}
        self.stat_max_vol = {}

    def update_stat_volume_max(self):
        res = {}
        for frame in conf_time_frames:
            _max = 0
            for candle in self.clusters[frame]:
                for rate in candle['rates']:
                    if candle[rate]['sum']['amount'] > _max:
                        _max = candle[rate]['sum']['amount']
            res[frame] = _max
        self.stat_max_vol = res

    def public_trades_maintainance(self):
        self.data_start_time = update_data_start_time()
        if conf_indicators_clusters:
            self.truncate_clusters()
            self.update_stat_volume_max()

    def truncate_clusters(self):
        begin = find_first_candle_time()
        while True:
            if not self.lock_clusters:
                self.lock_clusters = True
                for frame in conf_time_frames:
                    for i in range(len(self.clusters[frame])):
                        if self.clusters[frame][i]['timestamp'] > begin:
                            self.clusters[frame] = self.clusters[frame][i:]
                            break
                self.lock_clusters = False
                break

    def initialize(self):
        # Poloniex отдает данные в обратном порядке 1000 записей до ограничителя to. Первая строка - самая свежая
        to = int(time())
        self.clusters_initial()
        self.is_updated = True
        self.update_stat_volume_max()

    def clusters_initial(self):
        if conf_indicators_clusters:
            _rates = [i['rate'] for i in self.data]
            _rate_min = min(_rates)
            _rate_max = max(_rates)
            for frame in conf_time_frames:
                self.rate_step[frame] = round((_rate_max - _rate_min) / conf_pairs[self.pair]['cluster'][frame], 8)     # шаг цены
            for i in self.data:
                self.update_clusters(i['date'], i['rate'], i['amount'], i['type'])

    def update_clusters(self, date, rate, amount, typ):
        if conf_indicators_clusters:
            while True:
                if not self.lock_clusters:
                    self.lock_clusters = True
                    for frame in conf_time_frames:  # перебираем активные таймфреймы
                        if date >= self.data_start_time[frame]:
                            now = find_candle_start_time(date, conf_time_frames[frame])   # для каждого фрейма свой
                            pos = find_rate_cluster_position(rate, self.rate_step[frame])  # rate position
                            _ = self.clusters[frame]
                            if not _:   # если фрейм не имеет записей
                                _.append(
                                    {
                                        'timestamp': now,
                                        'date': utc_timestamp_to_date(now),
                                        'rates': {pos}, pos: get_cluster_structure()
                                     })

                            if _[-1]['timestamp'] != now:   # если фрейм не имеет текущей даты
                                _.append(
                                    {
                                        'timestamp': now,
                                        'date': utc_timestamp_to_date(now),
                                        'rates': {pos}, pos: get_cluster_structure()
                                    })
                            else:   # обновление свечи, если она уже есть
                                if not _[-1].get(pos):  # если отсутствует ценовой кластер
                                    _[-1]['rates'].add(pos)
                                    _[-1][pos] = get_cluster_structure()

                            _[-1][pos][typ]['count'] += 1
                            _[-1][pos][typ]['amount'] += amount

                            _[-1][pos]['sum']['amount'] += amount
                            _[-1][pos]['sum']['count'] += 1

                            _[-1][pos]['diff']['count_percent'] = percent_of_sum(_[-1][pos]['buy']['count'], _[-1][pos]['sell']['count'], 0)
                            _[-1][pos]['diff']['amount_percent'] = percent_of_sum(_[-1][pos]['buy']['amount'], _[-1][pos]['sell']['amount'], 0)

                self.lock_clusters = False
                break


def get_formatted_trades(date: int, trade_id: int, typ: int, rate: float, amount: float) -> dict:
    return {'date': date, 'id': trade_id, 'type': typ, 'rate': rate, 'amount': amount}


def find_rate_cluster_position(rate, step):
    try:
        return (rate // step) * step
    except ZeroDivisionError:
        pass


def get_cluster_structure():
    return {
        'buy': {'amount': 0, 'count': 0},
        'sell': {'amount': 0, 'count': 0},
        'diff': {'amount_percent': 0, 'count_percent': 0},
        'sum': {'amount': 0, 'count': 0},
    }


def update_data_start_time():
    return {i: int(time()) - conf_display_candles * conf_time_frames[i] for i in conf_time_frames}
