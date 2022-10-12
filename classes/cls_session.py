from config import *
from inc.inc_functions import add_percent, weighted_average, percent
from inc.inc_system import to8, ro2, time
from classes.cls_file_io import FileIO


#   все суммы в BTC
#   {'totalValue': 0.0, 'pl': 0.0, 'lendingFees': 0.0, 'netValue': 0.0, 'totalBorrowedValue': 0.0, 'currentMargin': 1.0}
#   {'totalValue': 0.00229803, 'pl': 0.0, 'lendingFees': 0.0, 'netValue': 0.00229803, 'totalBorrowedValue': 0.0, 'currentMargin': 1.0}  чистый баланс, нет позиций
#   {'totalValue': 0.00229803, 'pl': 0.0, 'lendingFees': 0.0, 'netValue': 0.00229803, 'totalBorrowedValue': 0.00191889, 'currentMargin': 1.19758297} - стоит ордер
#   {'totalValue': 0.00232033, 'pl': -2.456e-05, 'lendingFees': 0.0, 'netValue': 0.00229577, 'totalBorrowedValue': 0.00192899, 'currentMargin': 1.19014095} - куплено
# totalValue            Total margin value in BTC.
# pl                    Unrealized profit and loss in BTC.
# lendingFees           Unrealized lending fees in BTC.
# netValue              Net value in BTC.
# totalBorrowedValue    Total borrowed value in BTC.
# currentMargin         The current margin ratio.


# if res:
#     self.margin_total = float(res['totalValue'])
#     self.margin_profit = float(res['pl'])
#     self.margin_fees = float(res['lendingFees'])
#     self.margin_net = float(res['netValue'])
#     self.margin_borrowed = float(res['totalBorrowedValue'])
#     self.margin_margin = float(res['currentMargin'])
#     self.is_margin_updated = True
#     pprint(res)

class Sessions(FileIO):
    def __init__(self, private_trades, private_orders, pairs, charts, glob, coins, log):
        super().__init__()
        self.log = log
        # self.charts = charts
        self.private_trades = private_trades
        self.private_orders = private_orders
        self.pairs = pairs
        self.glob = glob
        self.coins = coins
        self.stop_list = ('glob', 'log', 'private_trades', 'private_orders', 'charts', 'pairs', 'coins', 'stop_list')

        clean_session = self.load_session()

        if clean_session:
            # self.log.log(self.pair, 'creating clean session')
            self.pair = None
            self.is_active = False              # сессия открыта - закрыта

            self.timestamp = 0                  # время последнего изменения сессии
            self.position_type = ''             # тип позиции long / sort (сессия открыта для вхождения в long / short)
            self.position_amount = ''           # фактический amount позиции
            self.position_filled = False        # позиция полностью набрана / нет

            self.time_open = 0                  # время открытия сессии
            self.time_close = 0                 # время закрытия сессии
            self.amount_wanted = 0              # сумма, которую изначально желаем купить

            self.orders_dict = {}               # словарь ордеров сессии
            self.open_order = 0                 # id текущего открытого ордера
            self.order_amount_initial = 0       # первоначальная сумма ордера
            self.order_amount = 0               # текущий объем ордера
            self.order_rate = 0                 # текущий курс ордера

            self.in_score = 0                   # скоринг buy сесии
            self.in_time_begin = 0              # время начала вхождения в позицию
            self.in_time_finish = 0             # время конца вхождения в позицию
            self.in_rate = 0                    # rate расчетной точки входа
            self.in_rate_mean = 0               # средневзвешенный курс входа
            self.in_rate_cancel = 0             # курс отмены слежения при поиске точки входа (закрывает сессию)

            self.out_score = 0                  # скоринг sell сессии
            self.out_time_begin = 0             # время начала выхода из позиции
            self.out_time_finish = 0            # время конца выхода из позиции
            self.out_rate = 0                   # rate закрытия позиции
            self.out_rate_mean = 0              # средневзвешенный rate закрытия позиции

            self.rate_stop_loss = 0             # rate stop loss (устанавливается при входе в позицию)
            self.rate_take_profit = 0           # rate закрытия позиции по take profit (зависит от стратегии)

            self.session_trades = []            # трейды в рамках сессии
            self.session_profit = 0             # профит всей сессии

    def add_score(self, data):
        if data and self.position_type == 'long':
            self.out_score += data['score']
        if data and self.position_type == 'short':
            self.in_score += data['score']

    def new_session_long(self, pair):
        self.pair = pair
        self.is_active = True
        if log_debug_sessions:
            self.log.log(self.pair, 'creating buy session')

        if self.open_order:
            self.private_orders.cancel_all_private_orders()
        self.open_order = 0
        self.order_amount_initial = 0
        self.order_amount = 0
        self.order_rate = 0

        self.position_type = 'long'
        self.amount_wanted = self.calculate_wanted_amount_rated()
        self.timestamp = int(time())
        self.time_open = int(time())
        self.in_rate = self.pairs.bid_rate
        self.in_rate_cancel = add_percent(self.pairs.bid_rate, conf_buy_cancel)
        self.rate_stop_loss = add_percent(self.pairs.bid_rate, conf_stop_loss)
        self.log.private_trades('{} new buy session rate {} ask {} bid {}'.format(self.pair, self.pairs.rate, self.pairs.ask_rate, self.pairs.bid_rate))
        self.save_session()

    def new_session_short(self, pair):
        self.pair = pair
        self.is_active = True
        if log_debug_sessions:
            self.log.log(self.pair, 'creating sell session')

        if self.open_order:
            self.private_orders.cancel_all_private_orders()
        self.open_order = 0
        self.order_amount_initial = 0
        self.order_amount = 0
        self.order_rate = 0

        self.position_type = 'long'
        self.timestamp = int(time())
        self.out_rate = max([self.charts.data['5m'][i]['high'] for i in [-1, -2, -3]])
        self.rate_stop_loss = add_percent(self.pairs.bid_rate, conf_stop_loss)
        self.out_time_begin = int(time())
        self.log.private_trades('{} new sell session rate {} ask {} bid {}'.format(self.pair, self.pairs.rate, self.pairs.ask_rate, self.pairs.bid_rate))
        self.save_session()

    def clear_session(self):
        if log_debug_sessions:
            self.log.log(self.pair, 'clearing session')
        self.is_active = False  # сессия открыта - закрыта
        self.timestamp = 0  # время последнего изменения сессии
        self.position_type = ''  # тип позиции long / sort (сессия открыта для вхождения в long / short)
        self.position_amount = ''  # фактический amount позиции
        self.time_open = 0  # время открытия сессии
        self.time_close = 0  # время закрытия сессии
        self.amount_wanted = 0  # сумма, которую изначально желаем купить
        self.orders_dict = {}  # словарь ордеров сессии
        self.open_order = 0  # id текущего открытого ордера
        self.order_amount_initial = 0  # первоначальная сумма ордера
        self.order_amount = 0  # текущий объем ордера
        self.order_rate = 0  # текущий курс ордера
        self.in_score = 0  # скоринг buy сесии
        self.in_time_begin = 0  # время начала вхождения в позицию
        self.in_time_finish = 0  # время конца вхождения в позицию
        self.in_rate = 0  # rate расчетной точки входа
        self.in_rate_mean = 0  # средневзвешенный курс входа (если позиция закуплена несколькими трейдами)
        self.in_rate_cancel = 0  # курс отмены слежения при поиске точки входа (закрывает сессию)
        self.out_score = 0  # скоринг sell сессии
        self.out_time_begin = 0  # время начала выхода из позиции
        self.out_time_finish = 0  # время конца выхода из позиции
        self.out_rate = 0  # rate закрытия позиции
        self.out_rate_mean = 0  # средневзвешенный rate закрытия позиции
        self.rate_stop_loss = 0  # rate stop loss (устанавливается при входе в позицию)
        self.rate_take_profit = 0  # rate закрытия позиции по take profit (зависит от стратегии)
        self.session_trades = []  # трейды в рамках сессии
        self.session_profit = 0  # профит всей сессии

    def show(self):
        return {att: self.__dict__[att] for att in self.__dict__ if att not in self.stop_list}

    def finish_buy_stage(self):     # процедура полного завершения закупки и переход к продаже
        if self.open_order:
            self.private_orders.cancel_all_private_orders()
        self.open_order = 0
        self.order_amount_initial = 0
        self.order_amount = 0
        self.order_rate = 0

        self.amount_wanted = self.calculate_wanted_amount_rated()
        self.is_buy_active = False
        self.type = 'sell'
        self.timestamp = int(time())
        self.in_time_finish = int(time())
        self.out_time_begin = int(time())
        self.upd_sess_stop_loss()
        self.upd_sess_floating_rates()
        self.save_session()

    def interrupt_buy_stage(self):     # прерывание закупки из-за ухода цены
        if self.open_order:
            self.private_orders.cancel_all_private_orders()
        self.open_order = 0
        self.order_amount_initial = 0
        self.order_amount = 0
        self.order_rate = 0
        self.is_buy_active = False
        self.upd_sess_stop_loss()
        self.upd_sess_floating_rates()
        self.save_session()

    def finish_sell_stage(self):
        self.timestamp = int(time())
        if self.open_order:
            self.private_orders.cancel_all_private_orders()
        self.open_order = 0
        self.order_amount_initial = 0
        self.order_amount = 0
        self.order_rate = 0
        self.out_time_finish = int(time())
        self.amount_out = self.coins.balance_total_rated(self.pairs.coin, self.pairs.rate)
        self.close_session()

    def load_session(self):
        data = self.load_zipped_file('save/session.dat')
        if data:
            if data['is_active']:
                print(data)
                [self.__setattr__(att, data[att]) for att in data]
                # self.log.log(self.pair, 'Session loaded from file')
                if self.orders_dict:
                    for i in self.orders_dict:
                        self.glob.add_order_params(i, self.pair, self.orders_dict[i]['type'])
                return False
        # self.log.log(self.pair, 'Session init -> no session file')
        return True

    def save_session(self):
        self.timestamp = int(time())
        data = {att: self.__dict__[att] for att in self.__dict__ if att not in self.stop_list}
        self.save_zipped_file('save/session.dat', data)

    def close_session(self):
        if log_debug_sessions:
            self.log.log(self.pair, 'closing session')
        # сохраняем в файл и обнуляем сессию
        self.time_close = int(time())
        self.session_profit = ro2(percent(self.in_rate_mean, self.out_rate_mean) - 2 * conf_market_fee)
        self.log.log_session_history(self.pair, self.show())

        if self.orders_dict:
            self.glob.mark_order_params_to_delete(self.orders_dict)
            # отмечаем связку ордер - пара на отложенное удаление

        if self.open_order:
            self.private_orders.cancel_private_order(self.open_order)

        # [delattr(self, att) for att in dir(self) if not att.startswith('_') and att not in self.stop_list]
        self.clear_session()
        if self.session_trades:
            self.log.private_trades('{} session closed, bought {} sold {} profit {}%'.format(self.pair, self.pairs.rate, self.pairs.ask_rate, self.session_profit))
        else:
            self.log.private_trades('{} session closed, bought {} sold {} profit {}%'.format(self.pair, self.pairs.rate,
                                                                                             self.pairs.ask_rate,
                                                                                             self.session_profit))
        self.save_session()

    def check_initial_session_relevance(self):
        # проверяет коллизии в парах в случае, если бот простаивал
        if self.is_active:
            #   если сессия активна
            self.timestamp = int(time())
            self.open_order = 0
            self.order_amount_initial = 0
            self.order_amount = 0
            self.order_rate = 0
            if len(self.session_trades) != len(self.private_trades.data):
                self.log.log(self.pair, '!!!!!! session_relevance -> trades mismatch, reconstructing')
                self.session_trades = self.private_trades.get_session_trades()
                if self.coins.balance_total_rated(self.pairs.coin, self.pairs.rate) < self.pairs.amount_limit and self.session_trades[-1]['type'] == 'sell':
                    self.log.log(self.pair, '!!!!!! session_relevance -> low pair balance & last trade = sell')
                    self.time_close = self.out_time_finish = self.session_trades[-1]['date']
                    _, _, self.out_rate_mean = self.private_trades.get_session_last_sells_info()
                    self.close_session()
        else:
            #   если сессия не активна
            print('check_initial_session_relevance self.coins.balance_total_rated', self.coins.balance_total_rated(self.pairs.coin, self.pairs.rate))
            print('check_initial_session_relevance self.pairs.amount_limit', self.pairs.amount_limit)
            if self.coins.balance_total_rated(self.pairs.coin, self.pairs.rate) >= self.pairs.market_bound:
                # есть баланс, но нет сессии (сессия утеряна) - останавливаем закупи и продаем, т.к. нет входных данных
                self.is_active = True
                if log_debug_sessions:
                    #   если пара закуплена
                    self.log.log(self.pair, '!!!!!! session_relevance -> NO session & got balance')
                self.type = 'sell'
                self.timestamp = int(time())
                if self.private_trades.data:
                    #   собираем данные о покупках
                    self.in_time_finish, self.in_rate, self.in_rate_mean = self.private_trades.get_session_last_buys_info()
                    self.open_rate_min = self.pairs.rate if self.pairs.rate < self.in_rate else self.in_rate
                    self.in_rate_cancel = add_percent(self.in_rate, conf_buy_cancel)
                    self.rate_stop_loss = add_percent(self.in_rate_mean, conf_stop_loss)
                    if self.private_trades.data[-1]['type'] == 'sell':
                        #   собираем данные о продажах
                        self.out_time_begin, self.out_rate, self.out_rate_mean = self.private_trades.get_session_last_sells_info()
                        self.close_rate_max = self.pairs.rate if self.pairs.rate > self.out_rate else self.out_rate
                        self.close_rate_trigger = add_percent(self.out_rate, -0.05)
                    self.session_trades = self.private_trades.get_session_trades()
        print(self.show())
        self.save_session()

    def upd_sess_weighted_average_rate(self):
        for typ in ['buy', 'sell']:
            rates = [_['rate'] for _ in self.session_trades if _['type'] == typ]
            amounts = [_['amount'] for _ in self.session_trades if _['type'] == typ]
            if typ == 'buy' and rates:
                self.in_rate_mean = weighted_average(rates, amounts)
                if log_debug_sessions:
                    self.log.log(self.pair, 'upd_sess_weighted_average_rate -> buy_rate_mean: {}'.format(to8(self.in_rate_mean)))
            if typ == 'sell' and rates:
                self.out_rate_mean = weighted_average(rates, amounts)
                if log_debug_sessions:
                    self.log.log(self.pair, 'upd_sess_weighted_average_rate -> sell_rate_mean: {}'.format(to8(self.out_rate_mean)))

    def upd_sess_stop_loss(self):
        self.rate_stop_loss = add_percent(self.in_rate_mean, conf_stop_loss)
        if log_debug_sessions:
            self.log.log(self.pair, 'upd_sess_stop_loss -> sell_rate_stop_loss: {}'.format(to8(self.rate_stop_loss)))

    def upd_sess_floating_rates(self):
        if self.type == 'buy':
            if self.pairs.bid_rate < self.open_rate_min or self.open_rate_min == 0:
                self.open_rate_min = self.pairs.bid_rate
                self.open_rate_trigger = add_percent(self.open_rate_min, conf_buy_trigger)
                if log_debug_sessions:
                    self.log.log(self.pair, 'upd_sess_floating_rates -> buy_rate_min: {}, buy_rate_trigger {}'
                                 .format(to8(self.open_rate_min), to8(self.open_rate_trigger)))
        if self.type == 'sell':
            if self.pairs.ask_rate > self.close_rate_max:
                self.close_rate_max = self.pairs.ask_rate
                self.close_rate_trigger = add_percent(self.close_rate_max, -conf_sell_trigger)
                if log_debug_sessions:
                    self.log.log(self.pair, 'upd_sess_floating_rates -> sell_rate_max: {}, sell_rate_trigger {}'
                                 .format(to8(self.close_rate_max), to8(self.close_rate_trigger)))

    def upd_session_socket_n(self, order, typ, rate, amount, date, amount_init):
        if log_debug_socket_updates:
            self.log.log(self.pair, 'upd_session_by_socket_n <- order: {}, type: {}, '
                                    'rate: {} amount: {}, date: {}, amount_init: {}'
                         .format(order, typ, to8(rate), to8(amount), date, to8(amount_init)))
        if self.is_active:
            self.orders_dict[order] = {'date': date, 'type': typ}
            self.open_order = order
            self.timestamp = int(time())
            self.order_rate = rate
            if not self.order_amount_initial:
                self.order_amount_initial = amount
            self.order_amount = amount
            if not self.in_time_begin:
                self.in_time_begin = date
            if log_debug_socket_updates:
                self.log.log(self.pair, 'upd_session_by_socket_n -> {}'.format(self.show()))
        else:
            if log_debug_socket_updates:
                self.log.log(self.pair, 'upd_session_by_socket_n -> ignoring session:  is_active = False')

    def upd_session_socket_p(self, order, typ, rate, amount):
        if log_debug_socket_updates:
            self.log.log(self.pair, 'upd_session_by_socket_p <- order: {}, type: {}, rate: {} amount: {}'.format(order, typ, to8(rate), to8(amount)))
        date = int(time())
        self.orders_dict[order] = {'date': date, 'type': typ}
        self.open_order = order
        self.timestamp = int(time())
        self.order_rate = rate
        if not self.order_amount_initial:
            self.order_amount_initial = amount
        self.order_amount = amount
        if not self.in_time_begin:
            self.in_time_begin = date
        if log_debug_socket_updates:
            self.log.log(self.pair, 'upd_session_by_socket_p -> {}'.format(self.show()))

    def upd_sess_trade_socket_t(self, trade_id, rate, amount, fee, total, typ, order, date):
        if log_debug_socket_updates:
            self.log.log(self.pair, 'upd_sess_trade_by_sock_t <- trade_id: {}, rate :{}, amount: {}, '
                                    'fee: {}, total: {}, typ: {}, order: {}, date: {}'
                         .format(trade_id, to8(rate), to8(amount), to8(fee), total, typ, order, date))

        if self.is_active:
            if order in self.orders_dict:
                self.add_session_trade(trade_id, rate, amount, fee, total, typ, order, date)
                self.upd_sess_weighted_average_rate()
                self.log.private_trades('{} {} at {} amount {} fee {}'.format(self.pair, typ, rate, amount, to8(fee)))
                if log_debug_socket_updates:
                    self.log.log(self.pair, 'upd_sess_trade_by_sock_t -> session_trades: {}'.format(self.session_trades))
            else:
                self.log.log(self.pair, 'upd_sess_trade_by_sock_t -> unknown order: {}'.format(order))
        else:
            self.log.log(self.pair, 'upd_sess_trade_by_sock_t -> ignoring, NO active session')

    def add_session_trade(self, trade_id, rate, amount, fee, total, typ, order, date):
        self.session_trades.append({'trade_id': trade_id,
                                    'rate': rate,
                                    'amount': amount,
                                    'fee': fee,
                                    'total': total,
                                    'type': typ,
                                    'order': order,
                                    'date': date})

    def upd_sess_bal_socket_o(self, order, typ, amount):
        if log_debug_socket_updates:
            self.log.log(self.pair, 'upd_sess_bal_socket_o <- order: {}, type: {}, amount: {}'.format(order, typ, amount))

        if self.is_active:
            if order in self.orders_dict:
                if amount:
                    self.order_amount = amount
                else:
                    self.open_order = 0
                    self.order_amount = 0

            if log_debug_socket_updates:
                self.log.log(self.pair, 'upd_sess_bal_socket_o -> {}'.format(self.show()))
        else:
            if log_debug_socket_updates:
                self.log.log(self.pair, 'upd_sess_bal_socket_o -> ignoring, NO active session, order {}'.format(order))

    def calculate_wanted_amount_rated(self):
        # функционал на будущее, с динамическим определением объема торгов
        return self.pairs.amount_limit
