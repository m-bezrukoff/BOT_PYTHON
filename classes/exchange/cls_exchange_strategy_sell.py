class ExchangeSellTactic:
    def __init__(self, pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log):
        super().__init__(pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log)
        self.pair = pair
        self.glob = glob
        self.log = log
        self.pairs = pairs[pair]
        self.charts = charts[pair]
        self.session = session
        self.indicators = indicators[pair]
        self.sell_score = 0
        self.sell_score_data = {}

    def tactic_sell_moving_averages(self):
        if self.indicators.ema_f['5m'][-1] < self.indicators.ema_s['5m'][-1]:
            if self.indicators.ema_f['5m'][-2] > self.indicators.ema_s['5m'][-2]:
                print('fast 5m пересекла вниз slow 5m')
                if self.indicators.ema_f['15m'][-1] < self.indicators.ema_s['15m'][-1]:
                    if self.indicators.ema_f['15m'][-2] > self.indicators.ema_s['15m'][-2]:
                        print('fast 15m пересекла вниз slow 15m')
                        if self.indicators.ema_f['30m'][-1] < self.indicators.ema_s['30m'][-1]:
                            if self.indicators.ema_f['30m'][-2] > self.indicators.ema_s['30m'][-2]:
                                print('fast 30m пересекла вниз slow 30m')
                                return 1
        return 0
