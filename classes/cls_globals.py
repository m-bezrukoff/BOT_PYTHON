from config import *
from inc.inc_system import time, sleep
from os.path import abspath
from os import curdir
from classes.cls_file_io import FileIO


class Globals(FileIO):
    def __init__(self, shared):
        self.settings = self.load_settings()
        self.data = shared.Namespace()                   # shared memory для использования в процессах

        self.data.pair_by_id = {}                        # таблица соответствия id и названий всех пар в листинге, заполняется из initializer
        self.data.id_by_pair = {}                        # таблица соответствия id и названий всех пар в листинге, заполняется из initializer
        self.data.coin_by_pair = coin_by_pair()          # таблица соответствия пары текущей монете и базовой монете USDT_TRX -> TRX
        self.data.monitoring_pairs = {}                  # наблюдаемые пары, заполняется из coins
        self.data.monitoring_pair_ids = set()            # id наблюдаемых пар, заполняется из preload
        self.data.rotatable_pair_ids = set()             # id торгуемых пар, заполняется из preload
        self.data.order_params = {}
        self.data.stop_by = {'requests': False, 'closeApp': False}
        self.data.script_path = abspath(curdir).replace('\\', '/')
        self.data.display_pair = list(conf_pairs.keys())[0]
        self.data.display_timeframe = '5m'
        self.data.socket_last_update = 0

    def load_settings(self):
        data = self.load_zipped_file('save/settings.dat')
        return data if data else {}

    def save_settings(self):
        self.save_zipped_file('save/settings.dat', self.settings)

    def add_order_params(self, order, pair, typ):
        self.data.order_params[order] = {'pair': pair, 'type': typ, 'time': 0, 'del': False}

    def mark_order_params_to_delete(self, order_list):
        for i in order_list:
            self.data.order_params[i]['del'] = True
            self.data.order_params[i]['time'] = time()

    def delete_old_pair_params(self):
        for i in list(self.data.order_params):
            if time() - self.data.order_params[i]['time'] > 900 and self.data.order_params[i]['del']:
                print('выброшен ордер', i)
                del self.data.order_params[i]

    def pair_by_order(self, order):
        try:
            return self.data.order_params[order]['pair']
        except KeyError as err:
            print(f'---------------------- error pair_by_order {str(err)}')
            sleep(0.5)
            return self.data.order_params[order]['pair']

    def type_by_order(self, order):
        try:
            return self.data.order_params[order]['type']
        except KeyError as err:
            print(f'---------------------- error type_by_order {str(err)}')
            sleep(0.5)
            return self.data.order_params[order]['type']


def coin_by_pair():
    return {i: i.split('_')[0] if i.split('_')[0] != conf_base_coin else i.split('_')[1] for i in conf_pairs}
