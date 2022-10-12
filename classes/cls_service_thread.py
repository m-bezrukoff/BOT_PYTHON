from inc.inc_system import time_multiple, sleep, time, to8
from config import *
from classes.cls_system import System
# from classes.cls_pairs import update_cross_rate_by_request


class ServiceThread(System):
    def __init__(self, glob, api, pairs, public_orders, public_trades, charts, coins, balances,  private_orders, private_trades, log, thread_socket):
        super().__init__()
        self.glob = glob
        self.api = api
        self.pairs = pairs
        self.public_orders = public_orders
        self.private_orders = private_orders
        self.public_trades = public_trades
        self.private_trades = private_trades
        self.thread_socket = thread_socket
        self.charts = charts
        self.coins = coins
        self.balances = balances
        self.log = log

    def get_initial_update_ticker(self):
        for pair in self.glob.monitoring_pairs:
            self.pairs[pair].update_ticker(self.glob.preload['ticker'][pair])

    def get_initial_orders_all_pairs(self):
        res = self.api.get_orders()
        if res:
            for pair in conf_pairs:
                if res[pair]:
                    self.private_orders[pair].add_private_orders(res[pair])
                self.private_orders[pair].is_updated = True

    def charts_update_all_pairs(self, candles):
        for pair in conf_pairs:
            self.charts[pair].update_public_trades_by_request(candles)

    def reconnect_and_reload(self):
        self.thread_socket.reconnect()
        for pair in conf_pairs:
            self.public_trades[pair].refresh_after_reconnect()

    def run(self):
        sleep(3)
        self.get_initial_update_ticker()
        self.get_initial_orders_all_pairs()

        while True:
            # тикер обновляется по сокету
            if self.glob.stop_by['closeApp']:
                break

            if time() - self.glob.socket_last_update > 5:
                self.log.error('socket is down for 5 sec. reconnecting...')
                self.reconnect_and_reload()

            if time_multiple(300, 120):
                # обновления данных каждые 180 сек
                self.log.save_logs()    # сохраняем логи
                self.charts_update_all_pairs(10)   # обновляем 10 свечей

            if time_multiple(300):
                # обновления данных каждые 5 мин
                self.glob.delete_old_pair_params()
                for pair in conf_pairs:
                    self.public_trades[pair].public_trades_maintainance()

            if time_multiple(3603):
                # обновления данных каждые 60 мин
                for pair in conf_pairs:
                    self.charts[pair].charts_truncate()

            sleep(0.95)
