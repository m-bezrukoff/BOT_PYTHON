from config import *
from classes.exchange.cls_exchange_strategy_buy import ExchangeBuyTactic
from classes.exchange.cls_exchange_strategy_sell import ExchangeSellTactic
from inc.inc_system import to8, ro8, to2, time
from inc.inc_functions import percent


class ExchangeStrategy(ExchangeBuyTactic, ExchangeSellTactic):
    def __init__(self, pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log):
        super().__init__(pair, glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, session, indicators, private_trades, log)
        self.pair = pair
        self.glob = glob
        self.api = api
        self.pairs = pairs[pair]
        self.charts = charts[pair]
        self.session = session
        self.log = log

    def exchange_strategy_buy_searching(self):
        if self.coins.balance_available(conf_base_coin) >= self.pairs.amount_limit:
            comment = ''
            score = 0
            self.log.log(self.pair, 'buy_searching -> open: {} high: {} low: {} close: {}'
                         .format(to8(self.charts.data['5m'][-1]['open']),
                                 to8(self.charts.data['5m'][-1]['high']),
                                 to8(self.charts.data['5m'][-1]['low']),
                                 to8(self.charts.data['5m'][-1]['close'])))

            score += self.tactic_buy_moving_averages()

            self.log.log(self.pair, 'buy_searching-> score: {} comment: {}'.format(round(score, 2), comment))

            if score >= 1 or debug_buy_anyway:     # сработал сигнал на переход к buy_tracking
                self.session.new_session()
        else:
            self.log.log(self.pair, 'Not enough money {}')

    def exchange_strategy_sell_searching(self):
        comment = ''
        score = 0
        self.log.log(self.pair, 'sell_searching ask {} max {} stop loss {} max->ask {}% profit {}%'
                     .format(to8(self.pairs.ask_rate),
                             to8(self.session.close_rate_max),
                             to8(self.session.rate_stop_loss),
                             to2(percent(self.session.close_rate_max, self.pairs.ask_rate)),
                             to2(percent(self.session.in_rate_mean, self.pairs.ask_rate))))

        self.log.log(self.pair, 'sell_searching-> score: {} comment: {}'.format(round(score, 2), comment))

        # score += self.sell_basic()
        score += self.tactic_sell_moving_averages()

        if score >= 1 or debug_sell_anyway:    # сработал сигнал на переход к sell_tracking
            self.session.new_session_short()

    def exchange_strategy_buy_tracking(self):
        if self.coins.balance_available(conf_base_coin) >= self.pairs.amount_limit:
            # strategy_buy_searching -> strategy_buy_tracking -> strategy_buy -> strategy_buy_escort -> strategy_buy_escort_price_cut -> strategy_move
            if self.session.is_active:
                self.log.log(self.pair, 'buy_tracking bid {} ask {} min {} trigger {} cancel {} min->bid {}%'
                             .format(to8(self.pairs.bid_rate),
                                     to8(self.pairs.ask_rate),
                                     to8(self.session.open_rate_min),
                                     to8(self.session.open_rate_trigger),
                                     to8(self.session.in_rate_cancel),
                                     to2(percent(self.session.open_rate_min, self.pairs.bid_rate))))

                if self.pairs.bid_rate < self.session.in_rate_cancel or debug_buy_anyway:
                    # покупаем пока цена не ушла выше buy_cancel
                    if self.pairs.bid_rate > self.session.open_rate_trigger or debug_buy_anyway:
                        # buy_rate_trigger сработал -> покупаем
                        if not self.session.open_order:
                            self.log.log(self.pair, 'buy tracking: now buy! bid_rate {} > buy_rate_trigger {}'
                                         .format(to8(self.pairs.bid_rate), to8(self.session.open_rate_trigger)))
                            if not self.session.open_order:
                                self.exchange_strategy_buy()
                        else:
                            self.log.log(self.pair, 'ERROR buy tracking: buy! but another order is here: {}'
                                         .format(self.session.open_order))
                else:
                    # цена ушла выше buy_cancel, отменяем покупки
                    if self.coins.balance_available_rated(self.pairs.coin, self.pairs.rate) < self.pairs.market_bound:
                        self.session.close_session()
                    else:
                        self.session.finish_buy_stage()
                        self.log.log(self.pair, 'buy_tracking: price too high, cancel! bid:{} > cancel:{}'
                                     .format(to8(self.pairs.bid_rate), self.session.in_rate_cancel))
            else:
                self.log.log(self.pair, 'strategy_buy_tracking -> NO active session!')
        else:
            self.log.log(self.pair, 'Not enough money {}')

    def exchange_strategy_sell_tracking(self):
        self.log.log(self.pair, 'sell_tracking ask {} max {} stop loss {} max->ask {}%'
                     .format(to8(self.pairs.ask_rate),
                             to8(self.session.close_rate_max),
                             to8(self.session.close_rate_trigger),
                             to2(percent(self.session.close_rate_max, self.pairs.ask_rate))))
        #   проверка на отсутские ордера уже пройдена
        if self.pairs.rate < self.session.close_rate_trigger:
            self.log.log(self.pair, 'sell_tracking: now sell! rate {} < sell_rate_trigger {}'
                         .format(to8(self.pairs.rate), to8(self.session.close_rate_trigger)))
            self.exchange_strategy_sell()

        if debug_sell_anyway:
            self.log.log(self.pair, 'sell_tracking -> sell testing')
            self.exchange_strategy_sell()

    def exchange_strategy_buy_escort(self):
        if self.coins.balance_available(conf_base_coin) >= self.pairs.amount_limit:
            self.log.log(self.pair, 'buy_escort bid {} ask {} min {} trigger {} cancel {} min->bid {}%'
                         .format(to8(self.pairs.bid_rate),
                                 to8(self.pairs.ask_rate),
                                 to8(self.session.open_rate_min),
                                 to8(self.session.open_rate_trigger),
                                 to8(self.session.in_rate_cancel),
                                 to2(percent(self.session.open_rate_min, self.pairs.bid_rate))))

            if self.pairs.bid_rate < self.session.in_rate_cancel or debug_buy_anyway:
                # покупаем пока цена ниже buy_cancel
                print('$1')
                if self.pairs.bid_rate != self.session.order_rate and not conf_rate_undercut:
                    print('$2')
                    if self.session.order_amount * self.pairs.rate > self.pairs.market_bound:   # move меньше 0.0001 не работает!
                        print('$3')
                        if self.pairs.bid_rate < self.pairs.ask_rate:
                            print('$4')
                            self.exchange_strategy_move(self.pairs.bid_rate)

                elif self.pairs.bid_rate > self.session.order_rate and conf_rate_undercut:      # если нас обошли
                    print('$5')
                    self.exchange_strategy_buy_escort_price_cut()

                elif self.pairs.bid_rate == self.session.order_rate and conf_rate_undercut:    # если мы в топе
                    # (биржа возвращает order_rate 0.0007906500000000001)
                    print('$6')
                    if ro8(self.pairs.bid_amount) == ro8(self.session.order_amount):   # если только мы в топе
                        print('$7 только мы в топе')
                        if time() - self.session.timestamp > 1.5:  # если нет активной борьбы
                            print('$8')
                            if (self.pairs.bid_2nd_rate + 0.00000001) < self.pairs.ask_rate:
                                # если подрезанная bid_2nd_rate меньше противоположной ask_rate
                                rate = self.pairs.bid_2nd_rate + 0.00000001
                                print('$9')
                                if rate < self.pairs.bid_rate:
                                    # если подрезанная _bid_2nd_rate больше себя (есть ли смысл подрезать)
                                    print('$10')
                                    if (self.session.order_amount * self.pairs.rate) > self.pairs.market_bound:
                                        # amount_rated = self.sessions.order_amount * self.pairs.rate
                                        print('$11')
                                        self.exchange_strategy_move(rate)
                                    else:
                                        print('$12 - нет валюты, отменяем. amount_rated')
                        else:
                            print('$13 - активная борьба, игнорим')
                    elif self.pairs.bid_amount / self.session.order_amount > 0.9:  # не только мы в топе!
                        print('$14 не только мы в топе, большой amount {} != {}'.format(self.pairs.bid_amount, self.session.order_amount))
                        self.exchange_strategy_buy_escort_price_cut()
                    else:   # не только мы в топе, amount незначительный, не дергаемся
                        print('$15 не только мы в топе, amount незначительный, не дергаемся')
                        print('_bid_amount: {} _order_amount: {}'.format(self.pairs.bid_amount, self.session.order_amount))
                else:
                    print('$16 не паримся, мы в топе')
            else:
                # цена выше buy_cancel
                print('$17')
                if self.coins.balance_available_rated(self.pairs.coin, self.pairs.rate) < self.pairs.market_bound:
                    print('$18')
                    self.session.interrupt_buy_stage()
                else:
                    print('$19')
                self.session.interrupt_buy_stage()
        else:
            self.log.log(self.pair, 'Not enough money {}')

    def exchange_strategy_sell_escort(self):
        self.log.log(self.pair, 'sell_escort ask {} max {} trigger {} max->ask {}% profit {}%'
                     .format(to8(self.pairs.ask_rate),
                             to8(self.session.close_rate_max),
                             to8(self.session.close_rate_trigger),
                             to2(percent(self.session.close_rate_max, self.pairs.ask_rate)),
                             to2(percent(self.session.in_rate_mean, self.pairs.ask_rate))))

        if self.pairs.ask_rate != self.session.order_rate and not conf_rate_undercut:
            print('$1')
            if self.session.order_amount * self.pairs.rate > self.pairs.market_bound:   # move меньше 0.0001 не работает!
                print('$2')
                if self.pairs.ask_rate > self.pairs.bid_rate:
                    print('$3')
                    self.exchange_strategy_move(self.pairs.ask_rate)

        if self.pairs.ask_rate < self.session.order_rate and conf_rate_undercut:
            # если наш ордер обошли
            print('$4')
            self.exchange_strategy_sell_escort_price_cut()

        elif self.pairs.ask_rate == self.session.order_rate and conf_rate_undercut:
            # если мы в топе (биржа возвращает order_rate 0.0007906500000000001 ?????????????????????????)
            print('$5')
            if ro8(self.pairs.ask_amount) == ro8(self.session.order_amount):
                # если только мы в топе
                print('$6')
                if time() - self.session.timestamp > 1.5:
                    # поднимается ко второй позиции только если нет активной борьбы
                    print('$7')
                    rate = self.pairs.ask_2nd_rate - 0.00000001
                    if rate > self.pairs.bid_rate:
                        # если подрезанная ask_2nd_rate больше противоположной bid_rate
                        print('$8')
                        if rate > self.pairs.ask_rate:
                            print('$9')
                            # если подрезанная ask_2nd_rate больше себя (есть ли смысл подрезать)
                            if self.session.order_amount * self.pairs.rate > self.pairs.market_bound:
                                print('$10')
                                self.exchange_strategy_move(rate)  # move меньше 0.0001 не работает!
                else:
                    print('$11 - активная борьба, игнорим')
            elif self.pairs.ask_amount / self.session.order_amount > 0.9:
                print('$12 не только мы в топе, большой amount {} != {}'
                      .format(self.pairs.ask_amount, self.session.order_amount))
                self.exchange_strategy_sell_escort_price_cut()
            else:
                # не только мы в топе, amount незначительный, не дергаемся
                print('$13 не только мы в топе, amount незначительный, не дергаемся')
        else:
            print('$14 не паримся, мы в топе')

    def exchange_strategy_buy_escort_price_cut(self):
        rate = self.exchange_calculate_buy_sell_rate('buy')
        print('$$1', 'rate:', to8(rate))

        if ro8(self.pairs.bid_amount) != ro8(self.session.order_amount):   # не подрезаем сами себя
            print('$$2')
            amount_rated = self.session.order_amount * self.pairs.rate
            if amount_rated > self.pairs.market_bound:
                print('$$3')
                if rate < self.pairs.ask_rate:
                    print('$$4')
                    if rate != self.session.order_rate:
                        print('$$5')
                        self.exchange_strategy_move(rate)
            else:
                print('$$6 !!!!!!!!!!!!!! amount_rated {} < 0.0001 -> raising amount'.format(to8(amount_rated)))
                self.exchange_strategy_move(rate, conf_trade_bounds[conf_base_coin]['amount_limit'])

    def exchange_strategy_sell_escort_price_cut(self):
        rate = self.exchange_calculate_buy_sell_rate('sell')
        print('$$11', 'rate:', to8(rate))

        if ro8(self.pairs.ask_amount) != ro8(self.session.order_amount):   # не подрезаем сами себя
            print('$$12')
            amount_rated = self.session.order_amount * self.pairs.rate
            if amount_rated > self.pairs.market_bound:
                print('$$13')
                if rate > self.pairs.bid_rate:
                    print('$$14')
                    if rate != self.session.order_rate:
                        print('$$15')
                        self.exchange_strategy_move(rate)
            else:
                print('$$16 !!!!!!!!!!!!!! amount_rated {} < 0.0001 -> close session'.format(to8(amount_rated)))
                self.session.finish_sell_stage()

    def exchange_strategy_buy(self):
        if conf_allow_buy:
            if not self.session.open_order:
                rate = self.exchange_calculate_buy_sell_rate('buy')
                amount = ro8(self.pairs.amount_limit / rate)
                res = self.api.buy(self.pair, to8(rate), amount)
                if res:
                    self.log.log(self.pair, 'buy order: {}'.format(res))
            else:
                self.log.log(self.pair, 'buy order -> error: another open order in session')
        else:
            self.log.log(self.pair, 'buy operations restricted by config!')

    def exchange_strategy_sell(self):
        if conf_allow_sell:
            if not self.session.open_order:
                rate = self.exchange_calculate_buy_sell_rate('sell')
                amount = self.coins.balance_available(self.pairs.coin)
                res = self.api.sell(self.pair, to8(rate), to8(amount))
                if res:
                    self.log.log(self.pair, 'sell order: {}'.format(res))
            else:
                self.log.log(self.pair, 'sell order -> error: another open order in session')
        else:
            self.log.log(self.pair, 'sell operations restricted by config!')

    def exchange_strategy_move(self, rate, amount=None):
        order = self.session.open_order
        res = self.api.move(order, to8(rate), self.pair, amount=amount)
        if res:
            if res['success'] == 1:
                self.log.log(self.pair, 'Order moved! {} -> {} rate: {}'.format(order, res['orderNumber'], to8(rate)))
            else:
                self.log.log(self.pair, 'Order move FAILED! {} {}'.format(order, res.__repr__()))
        else:
            self.log.log(self.pair, 'Order move FAILED! {}'.format(order))

    def exchange_calculate_buy_sell_rate(self, typ):
        if typ in conf_sell_idx:
            sell_rate = self.pairs.ask_rate - 0.00000001
            return sell_rate if sell_rate > self.pairs.bid_rate and conf_rate_undercut else self.pairs.ask_rate
        else:
            bid_rate = self.pairs.bid_rate + 0.00000001
            return bid_rate if bid_rate < self.pairs.ask_rate and conf_rate_undercut else self.pairs.bid_rate

    def exchange_strategy_stop_loss(self):
        self.log.log(self.pair, 'strategy_stop_loss')

        if self.session.type == 'buy':
            self.session.finish_buy_stage()

        if not self.session.is_sell_active:
            self.session.new_session_short()

        self.exchange_strategy_sell()


    def exchange_strategy_detector(self):
        balance_rated = self.coins.balance_total_rated(self.pairs.coin, self.pairs.rate)
        self.log.log(self.pair, 'bid {} ask {} rate {} amount {} {}'
                     .format(to8(self.pairs.bid_rate), to8(self.pairs.ask_rate),
                             to8(self.pairs.rate), balance_rated, conf_base_coin))

        # self.log.log(self.pair, 'available: {} onOrders: {} totalBtc: {} {} available: {}'
        #              .format(to8(self.coins.balance_available(self.pairs.coin)),
        #                      to8(self.coins.balance_on_orders(self.pairs.coin)),
        #                      to8(self.coins.balance_total_btc(self.pairs.coin, self.pairs.rate)),
        #                      conf_base_coin,
        #                      to8(self.coins.balance_available(conf_base_coin))))

        if self.session.is_active:
            self.log.log(self.pair, self.session.show())

        if self.session.is_active:

            # обработка stop_loss - срочно продаем!
            if balance_rated > self.pairs.market_bound:
                if self.pairs.rate < self.session.rate_stop_loss:
                    self.log.log(self.pair, '@0 strategy_detector -> strategy_stop_loss')
                    self.exchange_strategy_stop_loss()

            if self.session.type == 'buy':
                if self.session.is_buy_active:
                    #   если активна текущая фаза покупки
                    self.log.log(self.pair, '@1 strategy_detector -> buy')
                    amount_to_buy = self.session.amount_wanted * 0.97 - balance_rated
                    if amount_to_buy > self.pairs.market_bound or balance_rated < self.pairs.market_bound:
                        self.log.log(self.pair, '@2 strategy_buy_detector need more: {} {}'.format(to8(amount_to_buy), conf_base_coin))
                        if self.session.open_order:
                            self.log.log(self.pair, '@3 strategy_buy_escort')
                            self.exchange_strategy_buy_escort()
                        else:
                            self.log.log(self.pair, '@4 strategy_buy_tracking')
                            self.exchange_strategy_buy_tracking()
                    else:
                        self.log.log(self.pair, '@5 finishing buy')
                        self.session.finish_buy_stage()
                else:
                    #   если НЕ активна текущая фаза покупки
                    self.log.log(self.pair, '@6 strategy_buy_searching')
                    self.exchange_strategy_buy_searching()

            elif self.session.type == 'sell':
                if self.session.is_sell_active:
                    #   если активна текущая фаза продажи
                    self.log.log(self.pair, '@7 strategy_detector -> sell')
                    if balance_rated > self.pairs.market_bound:
                        self.log.log(self.pair, '@8 strategy_sell_detector - balance {}'.format(balance_rated))
                        if self.session.open_order:
                            self.log.log(self.pair, '@9 strategy_sell_escort')
                            self.exchange_strategy_sell_escort()
                        else:
                            self.log.log(self.pair, '@10 strategy_sell_tracking')
                            self.exchange_strategy_sell_tracking()
                    else:
                        if self.session.open_order:
                            self.log.log(self.pair, '@11 strategy_sell_escort')
                            self.exchange_strategy_sell_escort()
                        else:
                            self.log.log(self.pair, '@12 finish_sell_stage balance {}'.format(balance_rated))
                            self.session.finish_sell_stage()
                else:
                    self.log.log(self.pair, '@13 strategy_sell_searching')
                    self.exchange_strategy_sell_searching()
            else:
                self.log.log(self.pair, '@14 strategy_sell_detector - sessions.type lost !!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        else:
            self.log.log(self.pair, '@15 no session')
            if balance_rated < self.pairs.market_bound:
                self.log.log(self.pair, '@16 strategy_buy_searching')
                self.exchange_strategy_buy_searching()
            else:
                self.log.log(self.pair, '@17 strategy_sell_searching')
                self.exchange_strategy_sell_searching()
