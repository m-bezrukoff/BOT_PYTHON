from config import *
from classes.margin.cls_margin_strategy_long import MarginBuyTactic
from classes.margin.cls_margin_strategy_short import MarginSellTactic
from inc.inc_system import to8, ro8, to2, time, find_candle_start_time
from inc.inc_functions import percent


class MarginStrategy(MarginBuyTactic, MarginSellTactic):
    def __init__(self, pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log):
        super().__init__(pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log)
        self.pair = pair
        self.glob = glob
        self.log = log
        self.api = api
        self.session = session
        self.coins = coins
        self.balances = balances
        self.pairs = pairs[pair]
        self.charts = charts[pair]

        self.test_timestamp = 0
        self.points = []

    def margin_strategy_detector(self):
        pass
        # self.tma_strategy_find_open_long()
        # self.tma_strategy_find_open_short()
        # if self.session.is_active:                             # если активна сессия
        #     if self.session.position_filled:                   # если позиция набрана
        #         if self.session.position_type == 'long':
        #             self.search_long_exit_point()               # ищем точку выхода long позиции
        #         elif self.session.position_type == 'short':
        #             self.search_short_exit_point()              # ищем точку выхода short позиции
        #     else:
        #         if self.session.position_type == 'long':
        #             self.open_long_position()                  # добираем long позицию
        #         elif self.session.position_type == 'short':
        #             self.open_short_position()                 # добираем short позицию
        # else:
        #     if self.search_long_enter_point():
        #         self.open_long_position()
        #     if self.search_short_enter_point():
        #         self.open_short_position()

    def tma_strategy_find_open_long(self):
        t = find_candle_start_time(time(), conf_time_frames['5m'])
        if t > self.test_timestamp:
            if percent(self.indicators.tma_f['5m'][-3], self.indicators.tma_f['5m'][-2]) < 0:
                if percent(self.indicators.tma_f['5m'][-2], self.indicators.tma_f['5m'][-1]) > 0:
                    if self.indicators.bb_m_2['5m'][-1] > self.indicators.tma_f['5m'][-1]:
                        self.test_timestamp = t
                        self.log.log(self.pair, f'ENTER LONG rate: {to8(self.pairs.rate)} bid: {to8(self.pairs.bid_rate)} ask: {to8(self.pairs.ask_rate)}')
                        self.points.append({
                            'time': t,
                            'direction': 'long',
                            'type': 'open',
                            'marker': 9,
                            'rate': self.pairs.rate,
                            'bid': self.pairs.bid_rate,
                            'ask': self.pairs.ask_rate,
                        })
                        # save_zipped_pickle('log/test_trades_' + self.pair + '.dat', self.points)

    def tma_strategy_find_open_short(self):
        t = find_candle_start_time(time(), conf_time_frames['5m'])
        if t > self.test_timestamp:
            if percent(self.indicators.tma_f['5m'][-3], self.indicators.tma_f['5m'][-2]) > 0:
                if percent(self.indicators.tma_f['5m'][-2], self.indicators.tma_f['5m'][-1]) < 0:
                    if self.indicators.bb_m_2['5m'][-1] < self.indicators.tma_f['5m'][-1]:
                        self.test_timestamp = t
                        self.log.log(self.pair, f'ENTER SHORT rate: {to8(self.pairs.rate)} bid: {to8(self.pairs.bid_rate)} ask: {to8(self.pairs.ask_rate)}')
                        self.points.append({
                            'time': t,
                            'direction': 'short',
                            'type': 'open',
                            'marker': 10,
                            'rate': self.pairs.rate,
                            'bid': self.pairs.bid_rate,
                            'ask': self.pairs.ask_rate,
                        })
                        # save_zipped_pickle('log/test_trades_' + self.pair + '.dat', self.points)




    #
    # balance_rated = self.coins.balance_total_rated(self.pairs.coin, self.pairs.rate)    # баланс в основной валюте
    #
    # if self.glob.margin_session_active:     # допустима только одна
    #
    #
    #
    #
    #     # обработка stop_loss - срочно продаем!
    #     if balance_rated > self.pairs.market_bound:
    #         if self.pairs.rate < self.sessions.sell_rate_stop_loss:
    #             self.log.log(self.pair, '@0 strategy_detector -> strategy_stop_loss')
    #             self.exchange_strategy_stop_loss()
    #
    # else:   # сессии нет, ищем точку входа
    #     if self.margin_strategy_searching_long():
    #         return True
    #     if (self.indicators.ema_f[-2] < self.indicators.ema_s[-2]) and (self.indicators.ema_f[-1] > self.indicators.ema_s[-1]):     # пересечение скользящих
    #         self.open_margin_long_position()   # входим в лонг
    #
    #     if (self.indicators.ema_f[-2] > self.indicators.ema_s[-2]) and (self.indicators.ema_f[-1] > self.indicators.ema_s[-1]):     # пересечение скользящих
    #         self.open_margin_short_position()   # входим в шорт
