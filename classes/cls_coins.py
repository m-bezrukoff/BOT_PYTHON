from config import *


class Coins:
    def __init__(self, glob, log, preload):
        self.glob = glob
        self.log = log

        self.is_coins_updated = False
        self.coin_by_id = {i[1]['id']: i[0] for i in preload.data['coins'].items()}
        self.base_coin_pair_by_coin = {
            [coin for coin in pair.split('_') if coin != conf_base_coin][0]: pair for pair in preload.data['ticker'] if conf_base_coin in pair.split('_')
        }

        self.is_coins_updated = True

    # def balance_reserve(self):
    #     return ro8(self.balances[conf_base_coin]['available'])
    #
    # def balance_total(self, coin):
    #     return ro8(self.balances[coin]['available'] + self.balances[coin]['onOrders'])
    #
    # def balance_total_rated(self, coin, rate):
    #     return ro8((self.balances[coin]['available'] + self.balances[coin]['onOrders']) * rate)
    #
    # def balance_available(self, coin):
    #     return ro8(self.balances[coin]['available'])
    #
    # def balance_available_rated(self, coin, rate):           # баланс валюты в базовой валюте
    #     return ro8(self.balances[coin]['available'] * rate)
    #
    # def balance_on_orders(self, coin):
    #     return ro8(self.balances[coin]['onOrders'])
