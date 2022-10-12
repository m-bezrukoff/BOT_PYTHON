from config import *
from inc.inc_system import utc_date_to_timestamp, time, md5_hash
from statistics import mean
from classes.cls_file_io import FileIO
from classes.cls_api_poloniex_http import Api
from classes.cls_log import Log


class PrivateTrades(FileIO):
    def __init__(self, pair: str, api: Api, log: Log):
        self.pair = pair
        self.api = api
        self.log = log
        self.is_updated = False
        self.private_trades_path = 'save/private_trades_' + pair + '.dat'
        self.data = self.load_private_trades()
        self.initial_data_hash = md5_hash(self.data)
        self.lock = False

    def get_private_trades_by_request(self):
        to = int(time())
        fr = to - conf_public_trades_limit * 24 * 3600
        try:
            res = self.api.get_trades_private(self.pair, fr, to)
            if len(res) > 0:
                return res
            return []
        except Exception as e:
            print(e)
            self.get_private_trades_by_request()

    def add_private_trade_by_socket(self, trade_id, rate, amount, fee, total, typ, order, date):
        if log_debug_socket_updates:
            self.log.log(self.pair, 'add_private_trade <- trade_id: {}, rate :{}, amount: {}, fee: {}, total: {}, type: {}, order: {}, date: {}'
                         .format(trade_id, rate, amount, fee, total, typ, order, date))
        while True:
            if not self.lock:
                self.lock = True
                self.data.append(pt_return_private_trade_format(trade_id, rate, amount, fee, total, typ, order, date))
                self.lock = False
                break

        if log_debug_socket_updates:
            self.log.log(self.pair, 'add_private_trade -> self.data[-1]: {}'.format(self.data[-1]))

    def update_private_trades_by_request(self, res):
        ids = set([i['id'] for i in self.data])
        dat = []
        if res:
            for i in res:
                trade_id = int(i['tradeID'])
                rate = float(i['rate'])
                amount = float(i['amount'])
                fee = float(i['fee'])
                total = float(i['total'])
                typ = i['type']
                order = int(i['orderNumber'])
                date = utc_date_to_timestamp(i['date'][:19])      # 2020-06-25 14:35:19.000000

                if i['tradeID'] not in ids:
                    dat.append(pt_return_private_trade_format(trade_id, rate, amount, fee, total, typ, order, date))

            while True:
                if not self.lock:
                    self.lock = True
                    self.data.extend(dat)
                    self.data.sort(key=lambda k: k['date'])
                    self.lock = False
                    break

    def private_trades_initial_update(self):
        res = self.get_private_trades_by_request()

        if res:
            self.update_private_trades_by_request(res)
            while True:
                if not self.lock:
                    self.lock = True
                    self.data.sort(key=lambda k: k['date'])
                    self.lock = False
                    break
            self.truncate_private_trades()
            if self.initial_data_hash != md5_hash(self.data):
                self.save_private_trades()
        else:
            self.log.log(self.pair, 'private_trades_initial_update - {} no data'.format(self.pair))
        self.is_updated = True

    def truncate_private_trades(self):
        limit = time() - conf_public_trades_limit * 24 * 3600
        while True:
            if not self.lock:
                self.lock = True
                for i in self.data:
                    if i['date'] < limit:
                        self.data.remove(i)
                self.lock = False
                break

    def save_private_trades(self):
        self.save_zipped_file(self.private_trades_path, self.data)
        self.log.log(self.pair, f'Private trades {self.pair} saved to file')

    def load_private_trades(self):
        d = self.load_zipped_file(self.private_trades_path)
        if d:
            self.log.log(self.pair, f'Private trades {self.pair} loaded from file')
            return d
        return []

    def get_session_last_buys_info(self):
        print('get_session_last_buys_info ->', self.data)
        t = 0
        r = 0
        m = []
        for _ in reversed(self.data):
            if _['type'] == 'buy':
                print('get_session_last_buys_info ->', _)
                t = _['date']
                r = _['rate']
                m.append(_['rate'])
            else:
                if t:
                    break
        if m:
            print('get_session_last_buys_info ->', t, r, mean(m))
            return t, r, mean(m)
        else:
            return t, r, 0

    def get_session_last_sells_info(self):
        t = 0
        r = 0
        m = []
        for _ in reversed(self.data):
            if _['type'] == 'sell':
                t = _['date']
                r = _['rate']
                m.append(_['rate'])
            else:
                break
        return t, r, mean(m)

    def get_session_trades(self):
        x = []
        i = False
        for _ in reversed(self.data):
            if _['type'] == 'buy':
                i = True
                x.append(_)
            else:
                if i:
                    break
                x.append(_)
        return x


def pt_return_private_trade_format(trade_id, rate, amount, fee, total, typ, order, date):
    return {
            'id': trade_id,
            'rate': rate,
            'amount': amount,
            'fee': fee,
            'total': total,
            'type': typ,
            'order': order,
            'date': date,
        }
