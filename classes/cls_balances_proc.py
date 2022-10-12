from inc.inc_system import to8
from config import *


class BalancesOfProcess:
    def __init__(self, balances_data):
        self.data = balances_data

        print(self.data['exchange'])
        self.btc_pair_by_coin = {[coin for coin in pair.split('_') if coin != 'BTC'][0]: pair for pair in preload.data['ticker'] if 'BTC' in pair.split('_')}
        self.usd_pair_by_coin = {[coin for coin in pair.split('_') if coin != 'USDT'][0]: pair for pair in preload.data['ticker'] if 'USDT' in pair.split('_')}

    def balance(self, coin):
        return self.data[conf_market_type][coin]

    # def balance_in_btc(self, coin):     # баланс монеты в BTC
    #     if coin == 'BTC':
    #         return self.data[conf_market_type][coin]
    #     if self.btc_pair_by_coin[coin].split('_')[1] == coin:
    #         res = self.data[conf_market_type][coin] * self.pairs[self.btc_pair_by_coin[coin]].rate
    #     else:
    #         res = self.data[conf_market_type][coin] / self.pairs[self.btc_pair_by_coin[coin]].rate
    #     return res
    #
    # def balance_in_usd(self, coin):     # баланс монеты в USDT
    #     if coin == 'USDT':
    #         return self.data[conf_market_type][coin]
    #     if self.usd_pair_by_coin[coin].split('_')[1] == coin:
    #         res = self.data[conf_market_type][coin] * self.pairs[self.usd_pair_by_coin[coin]].rate
    #     else:
    #         res = self.data[conf_market_type][coin] / self.pairs[self.usd_pair_by_coin[coin]].rate
    #     return res

    # def market_total_btc_rated(self):   # всего на текущем типе рынка в BTC
    #     return sum([self.balance_in_btc(coin) for coin in self.data[conf_market_type]])
    #
    # def market_total_usd_rated(self):   # всего на текущем типе рынка в USD
    #     return sum([self.balance_in_usd(coin) for coin in self.data[conf_market_type]])
    #
    # def total_margin_value(self):   # всего на текущем типе рынка в BTC
    #     return self.market_total_btc_rated() * 0.99

