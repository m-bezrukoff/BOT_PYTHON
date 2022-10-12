from config import *
from classes.cls_dataclasses import SendApiMsg, ReceiveMsg
from classes.cls_file_io import FileIO


class Preload(FileIO):
    def __init__(self, glob, log, pipe_api, pipe_main):
        self.glob = glob
        self.log = log
        self.pipe_api = pipe_api
        self.pipe_main = pipe_main
        self.data = dict()

        self.data = self.load_zipped_file('save/preload.dat')
        # self.data['coins'], self.data['ticker'], self.data['balance'], self.data['margin_summary'] = self.preload_data()
        # self.save_zipped_file('save/preload.dat', self.data)

        self.glob.data.pair_by_id = {self.data['ticker'][pair]['id']: pair for pair in self.data['ticker']}
        self.glob.data.id_by_pair = {pair: self.data['ticker'][pair]['id'] for pair in self.data['ticker']}
        self.glob.data.rotatable_pair_ids = set([self.data['ticker'][pair]['id'] for pair in conf_pairs])

        self.monitoring_coins = set([i.split('_')[0] for i in conf_pairs] + [i.split('_')[1] for i in conf_pairs])
        self.monitoring_coins.update(set([i for i in self.data['balance']['exchange']]))  # добавляем в мониторинг монеты с exchange балансом
        self.monitoring_coins.update(set([i for i in self.data['balance']['margin']]))    # добавляем в мониторинг монеты с margin балансом

        self.glob.data.monitoring_pairs = self.get_cross_pairs(self.monitoring_coins)
        self.glob.data.monitoring_pair_ids = set([self.data['ticker'][pair]['id'] for pair in self.glob.data.monitoring_pairs])

    def preload_data(self):
        requests = {'get_coins': None, 'get_ticker': None, 'get_available_account_balances': None, 'get_margin_summary': None}
        for i in requests:
            SendApiMsg(pipe=self.pipe_api, action=i, reply='pipe_main')
        for i in requests:
            result = ReceiveMsg(self.pipe_main)
            if result.action in requests:
                requests[result.action] = result.data
        return requests.values()

    def get_cross_pairs(self, additive_coins):
        """
        используются для получения курсов к основным монетам: BTC и USDT
        (например для USDC_ETH нужны еще: USDT_USDC, USDT_ETH,
        """
        parts = [conf_bases[i] + '_' + conf_bases[i+1] for i in range(-1, len(conf_bases)) if i+1 < len(conf_bases)]
        parts += [i + '_' + x for i in additive_coins for x in conf_bases]
        parts += [x + '_' + i for i in additive_coins for x in conf_bases]
        return {i: True if i in conf_pairs else False for i in parts if i in self.data['ticker']}

