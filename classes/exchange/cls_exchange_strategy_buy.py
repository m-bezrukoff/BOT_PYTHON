class ExchangeBuyTactic:
    def __init__(self, pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log):
        super().__init__(pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log)
        self.pair = pair
        self.glob = glob
        self.log = log
        self.pairs = pairs[pair]
        self.charts = charts[pair]
        self.session = session
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

        # if ema_f < ema_s:
        #     if macd_in_h_2 < 0 < macd_in_h_1 and macd_in < 0:
        #         if (self.pairs.rate / ema_s) / (ema_f / ema_s) < 0.997:
        #             return 1
        # #   на растущем тренде
        # if ema_f > ema_s:
        #     if macd_in_h_2 < 0 < macd_in_h_1 and macd_in < 0:
        #         if (self.pairs.rate / ema_s) / (ema_f / ema_s) < 0.55:
        #             return 1

    # def tactic_buy_rsi(self):
    #     # не покупаем, если был бурный рост за последние 3 свечи
    #     if self.indicators.rsi_3[-1] > 50:  # только штрафуем!
    #         score = ro2((-self.indicators.rsi_3[-1]) / 100)
    #         self.buy_score += score
    #         self.buy_score_data['rsi {}%'.format(round(self.indicators.rsi_3[-1]))] = score

    # def tactic_buy_rsi(self):
    #     # не покупаем, если был бурный рост за последние 3 свечи
    #     if self.indicators.rsi[-1] < 20:  # только штрафуем!
    #         score = 1
    #         self.buy_score += score
    #         self.buy_score_data['rsi {}%'.format(round(self.indicators.rsi_7[-1]))] = score

    # def tactic_buy_macd(self):
    #     macd_3 = self.indicators.macd_h[-3]
    #     macd_2 = self.indicators.macd_h[-2]
    #     macd_1 = self.indicators.macd_h[-1]
    #     # print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
    #     if 0 > macd_1 > macd_2 and macd_2 < macd_3:
    #         # self.buy_score += score
    #         # self.buy_score_data['macd перелом минимума {}'.format(to2(macd_2))] = score
    #         msg = 'ask {} bid {} rate {} macd {} {} {} rsi {}'\
    #             .format(to8(self.pairs.ask_rate),
    #                     to8(self.pairs.bid_rate),
    #                     to8(self.pairs.rate),
    #                     to8(macd_1),
    #                     to8(macd_2),
    #                     to8(macd_3),
    #                     self.indicators.rsi[-1])
    #         self.log.save_signal(self.pair, msg)
    #         return 1
    #     return 0
    #
    # def tactic_by_triple_ema_diff(self):
    #     tma_h_3 = self.indicators.tma_hist[-3]
    #     tma_h_2 = self.indicators.tma_hist[-2]
    #     tma_h_1 = self.indicators.tma_hist[-1]
    #     wma_1 = self.indicators.wma[-1]
    #
    #     if 0 > tma_h_1 > tma_h_2 and tma_h_2 < tma_h_3:
    #         wma_diff = percent(wma_1, self.pairs.bid_rate)
    #         if wma_diff < -0.3:
    #             msg = 'ask {} bid {} rate {} tma_h_1 {} {} {} wma_diff {} rsi {}' \
    #                 .format(to8(self.pairs.ask_rate),
    #                         to8(self.pairs.bid_rate),
    #                         to8(self.pairs.rate),
    #                         to8(tma_h_1),
    #                         to8(tma_h_2),
    #                         to8(tma_h_3),
    #                         to2(wma_diff),
    #                         self.indicators.rsi[-1])
    #             self.log.save_signal(self.pair, msg)
    #             return 1
    #     return 0

    # def tactic_buy_macd(self):
    #     # effect = 1
    #     # threshold = -0.58
    #     score = 0.5
    #     macd_3 = self.indicators.macd_h[-3] * 100000
    #     macd_2 = self.indicators.macd_h[-2] * 100000
    #     macd_1 = self.indicators.macd_h[-1] * 100000
    #     if macd_2 < -0.2:     # macd перелом минимума
    #         if macd_3 > macd_2 < macd_1:
    #             # score = ro2((macd_2 * effect / threshold))
    #             # print(score, macd_2)
    #             self.buy_score += score
    #             self.buy_score_data['macd перелом минимума {}'.format(to2(macd_2))] = score
    #
    #     if macd_2 < 0 < macd_1:     # macd рост через 0
    #         if macd_3 <= macd_2 <= macd_1:
    #             # score = effect
    #             self.buy_score += score
    #             self.buy_score_data['macd переход в плюс {} {} {}'.format(to2(macd_3), to2(macd_2), to2(macd_1))] = score

    # def tactic_buy_ema(self):   # отклонение от ema
    #     # ищем сильную просадку от линии ema, штраф за близость к ema
    #     effect = 0.9
    #     threshold = -0.45
    #     dev = percent(self.indicators.ema_s[-1], self.charts.data[300][-1]['low'])
    #     score = ro2((-(1 + effect) * dev + threshold) / -threshold)
    #     self.buy_score += score
    #     self.buy_score_data['отклонение от ema {}%'.format(to2(dev))] = score
