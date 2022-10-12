from inc.inc_system import to8
from config import *
from stocks.poloniex.poloniex_functions import init_exchange_balaces


class Balances:
    """
        Poloniex spot market response:
        {'exchange': {'BTC': 0.00030523, 'BTT': 500.0, 'DAI': 0.40639393}, 'margin': {'BTC': 1e-08, 'TRX': 1381.0825858, 'USDT': 3.60507976}}

    """
    def __init__(self, glob, log, shared, coins, preload):
        self.glob = glob
        self.log = log
        self.coins = coins
        self.is_balances_updated = False

        self.data = shared.dict()
        self.data['exchange'] = init_exchange_balaces(shared, preload.data['balance']['exchange'])
        self.data['margin'] = init_exchange_balaces(shared, preload.data['balance']['margin'])
        # self.data['futures'] = init_exchange_balaces(shared, preload.data['balance']['futures'])

        print(self.data['exchange'])
        self.btc_pair_by_coin = {[coin for coin in pair.split('_') if coin != 'BTC'][0]: pair for pair in preload.data['ticker'] if 'BTC' in pair.split('_')}
        self.usd_pair_by_coin = {[coin for coin in pair.split('_') if coin != 'USDT'][0]: pair for pair in preload.data['ticker'] if 'USDT' in pair.split('_')}

        # self.balance_data = preload.data['balance']

        self.amount_on_orders = {}
        self.is_balances_updated = True

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

    def upd_balance_by_sock_b(self, coin, balance_change, wallet):
        if wallet == 'e':
            self.balance_data['exchange'][coin] += balance_change
        elif wallet == 'm':
            self.balance_data['margin'][coin] += balance_change
        elif wallet == 'l':
            self.log.error('lending balances not supported yet!')
        else:
            self.log.error(f'upd_coin_bal_by_sock_b -> unknown wallet type: {wallet}')

    def upd_balance_by_sock_o_n(self, pair, coin, amount, typ):
        if log_debug_socket_updates:
            self.log.log(f'{pair} upd_coin_bal_by_sock_o_n <- coin: {coin}, amount: {to8(amount)}, typ: {typ}')

        if typ in conf_sell_idx and coin != conf_base_coin:
            self.amount_on_orders[coin] = amount
            if log_debug_socket_updates:
                self.log.log(f'{pair} upd_coin_bal_by_sock_o_n -> {coin} [onOrders]: {to8(amount)}')
        else:
            if log_debug_socket_updates:
                self.log.log(f'{pair} upd_coin_bal_by_sock_o_n -> skip {conf_base_coin} onOrders')

    # def coin_balance_test_print(self, coin):
    #     print(f'{coin}: amount {to8(self.balance(coin))} in BTC: {to8(self.balance_in_btc(coin))} in USD: {to8(self.balance_in_usd(coin))}')
