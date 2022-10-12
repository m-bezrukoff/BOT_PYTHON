from inc.inc_functions import percent
from statistics import mean
from inc.inc_system import to8, ro8, to2, ro2, to16


class MarginBuyTactic:
    def __init__(self, pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log):
        super().__init__(pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log)
        self.pair = pair
        self.glob = glob
        self.log = log
        self.session = session
        self.pairs = pairs[pair]
        self.charts = charts[pair]
        self.indicators = indicators[pair]
        self.buy_score = 0
        self.buy_score_data = {}

    def buy_scoring(self):
        self.buy_score = 0
        self.buy_score_data = {}
        return self.buy_score, self.buy_score_data

    def tactic_buy_moving_averages(self):
        if self.indicators.ema_f['5m'][-1] > self.indicators.ema_s['5m'][-1]:
            if self.indicators.ema_f['5m'][-2] < self.indicators.ema_s['5m'][-2]:
                print('fast 5m пересекла вверх slow 5m')
                if self.indicators.ema_f['15m'][-1] > self.indicators.ema_s['15m'][-1]:
                    if self.indicators.ema_f['15m'][-2] < self.indicators.ema_s['15m'][-2]:
                        print('fast 15m пересекла вверх slow 15m')
                        if self.indicators.ema_f['30m'][-1] > self.indicators.ema_s['30m'][-1]:
                            if self.indicators.ema_f['30m'][-2] < self.indicators.ema_s['30m'][-2]:
                                print('fast 30m пересекла вверх slow 30m')
                                return 1
        return 0

    def search_long_enter_point(self):
        # if (self.indicators.ema_f[-2] < self.indicators.ema_s[-2]) and (self.indicators.ema_f[-1] > self.indicators.ema_s[-1]):  # пересечение скользящих
        #     return True
        return False

    def search_long_exit_point(self):
        return False

    def open_long_position(self):
        pass
