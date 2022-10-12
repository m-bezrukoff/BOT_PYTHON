from inc.inc_system import find_first_candle_time, time, show_taken_time, sleep, to2, utc_timestamp_to_date
from config import *
from classes.cls_file_io import FileIO
from classes._data_types import PublicTradeData
from pprint import pprint


class TradesPublic(FileIO):
    """
    ['t', '38444414', 0, '14826.63873565', '0.00006913', 1604782080]]]
    {"globalTradeID": 495739474, "tradeID": 38444414, "date": "2020-11-07 20:48:00", "type": "sell", "rate": "14826.63873565", "amount": "0.00006913", "total": "1.02496553", "orderNumber": 779496208636},

    ['t', '38444412', 1, '14828.32059438', '0.00134877', 1604782074]
    {"globalTradeID": 495739454, "tradeID": 38444412, "date": "2020-11-07 20:47:54", "type": "buy", "rate": "14828.32059438", "amount": "0.00134877", "total": "19.99999396", "orderNumber": 779496094750}

    в Poloniex public trades отдаются в обратном порядке, от последних к ранним
    в запросе https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_ETH&start=1612580400&end=1612569900
    не важна, очередность ОТ и ДО. Результат всегда возвращается 1000 записей от наиболее свежей даты.

    ###########################################
    #   ПРОВЕРИТЬ СООТВЕТСВИЕ ВАЛЮТ ОБЪЕМОВ !
    ###########################################
    """

    def __init__(self, pair, log, api):
        self.pair = pair
        self.log = log
        self.api = api
        self.public_trades_path = 'save/public_trades_' + pair + '.dat'
        self.data = self.pub_trades_load()  # публичные трейды
        self.data_start_time = update_data_start_time()
        self.is_updated = False
        self.lock_data = False

        self.rate_min = 0
        self.rate_max = 0
        self.rate_step = {i: 0 for i in conf_time_frames}
        self.stat_max_vol = {}

    def public_trades_maintenance(self):
        self.data_start_time = update_data_start_time()
        self.truncate_data()

    def add_public_trade_by_socket(self, date: int, trade_id: int, _type: int, rate: float, amount: float) -> None:
        while True:
            if not self.lock_data:
                self.lock_data = True
                self.data.append(PublicTradeData(date=date, id=trade_id, type=_type, rate=rate, amount=amount))
                self.lock_data = False
                break

    def truncate_data(self):
        begin = find_first_candle_time()
        while True:
            if not self.lock_data:
                self.lock_data = True
                for i in range(len(self.data)):
                    if self.data[i].date > begin:
                        self.data = self.data[i:]
                        break
                self.lock_data = False
                break

    def update_public_trades_by_request(self, fr: int, to: int) -> None:
        res = self.api.get_trades_public(self.pair, fr, to)
        print('RES', len(res), utc_timestamp_to_date(res[0].date), '-', utc_timestamp_to_date(res[-1].date))
        if res:
            while True:
                if not self.lock_data:
                    self.lock_data = True
                    t1 = time()
                    self.data.extend(res)
                    self.data = list({i.id: i for i in self.data}.values())  # удаляем дубликаты
                    self.data.sort(key=lambda k: k.id)
                    print(f'update_public_trades_by_request time {to2(time() - t1)}')
                    self.lock_data = False
                    break

    def public_trades_consistency(self):
        start = int(time()) - conf_total_candles * max(conf_time_frames.values())
        print('start date', utc_timestamp_to_date(start))
        for i in range(-1, -len(self.data) + 1, -1):
            if self.data[i].id - self.data[i - 1].id != 1:
                print('@1')
                print(self.data[i].__repr__())
                print(self.data[i - 1].__repr__())
                return self.data[i].date
        if self.data[0].date > start:
            print('@2')
            return self.data[0].date
        return False

    def initialize(self):
        """ Poloniex отдает данные в обратном порядке 1000 записей до ограничителя to. Первая строка - самая свежая """
        to = int(time())
        while to:
            self.update_public_trades_by_request(to - 60 * 60 * 24, to + 5)
            to = self.public_trades_consistency()
        self.save()
        self.is_updated = True

    def refresh_after_reconnect(self):
        to = int(time())
        self.update_public_trades_by_request(to - 3600, to + 5)

    def shutdown(self):
        self.truncate_data()
        self.save()

    def pub_trades_load(self):
        try:
            data = self.load_zipped_file(self.public_trades_path)
            if data:
                self.log.log(self.pair, f'Public trades {self.pair} loaded {len(data)} records')
                return data
        except EOFError:
            self.delete_file(self.public_trades_path)
        return []

    def save(self):
        self.save_zipped_file(self.public_trades_path, self.data)
        self.log.log(self.pair, f'Public trades {self.pair} saved')


def update_data_start_time():
    return {i: int(time()) - conf_display_candles * conf_time_frames[i] for i in conf_time_frames}
