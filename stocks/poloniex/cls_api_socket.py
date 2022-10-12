from threading import Thread
from PyQt6.QtCore import QThread
from websocket import WebSocketApp, enableTrace
from inc.inc_system import sleep, time, mktime, strptime, ro8, to2
from json import loads, dumps
from config import *

from hmac import new as _new
from urllib.parse import urlencode as _urlencode
from hashlib import sha512 as _sha512


class ApiSocket(QThread):
    def __init__(self, glob, log, api, coins, balances, pairs):
        super().__init__()
        self.glob = glob
        self.log = log
        self.api = api
        self.coins = coins
        self.balances = balances
        self.pairs = pairs
        self.problem_time = 0
        # enableTrace(True)

        self.ws = self.start_socket_client()

    def start_socket_client(self):
        self.log.socket('Opening connection')
        ws = WebSocketApp('wss://api2.poloniex.com/',
                          on_open=self.on_open,
                          on_message=self.on_message,
                          on_error=self.on_error,
                          on_close=self.on_close, )

        t = Thread(target=ws.run_forever, name='thread_sockets')
        t.daemon = True
        t.start()
        return ws

    def lets_make_error(self):
        if int(self.glob.socket_last_update) % 15 == 0:
            print('---- ВЫЗЫВАЕМ ОШИБКУ ----')
            self.on_error(self.on_error, 'KeyError')

    def on_error(self, obj, err):
        error = str(err.__repr__())
        self.problem_time = time()

        if 'is_ssl' in error:
            self.log.error_trace('socket reconnect failed')
            return False

        if 'WebSocketBadStatusException' in error:
            # 429, 502 - Bad gateway
            self.log.error_trace('socket error {} '.format(error))
            sleep(5)

        elif 'WebSocketConnectionClosedException' in error:
            self.log.error(error)
            self.reconnect()

        elif 'WebSocketTimeoutException' in error:
            self.log.error('socket: {}'.format(error))
            self.reconnect()

        elif 'KeyError' in error:
            self.log.error('{} KeyError - ignoring!'.format('+' * 40))
            self.log.error('socket: {}'.format(error))

        else:
            self.log.error_trace('unlisted socket error: {}'.format(error))
            sleep(1)
            self.reconnect()

    def on_message(self, obj, message):
        if self.problem_time:
            self.log.error(f'socket reconnected successfully in {to2(time() - self.problem_time)} s')
        self.glob.socket_last_update = time()
        # self.lets_make_error()
        # save_file('log/debug_socket.txt', message)
        try:
            json_msg = loads(message)
            if len(json_msg) > 2:
                self.msg_interpreter(json_msg)

        except KeyError as err:
            print('{} socket KeyError in on_message'.format('+' * 40))
            self.log.error('{} socket KeyError in on_message'.format('+' * 40))
            self.log.error(message)
            self.log.error(err.__repr__())

    def on_close(self, obj, _a, _b):
        print('closing api socket thread')
        pass

    def on_open(self, obj):
        self.log.socket('socket opened successfully')

        payload = {'nonce': next(self.api.rest_api.nonce_iter)}
        # payload = {'nonce': int(time() * 1000000000)}
        payload_encoded = _urlencode(payload)
        sign = _new(
            conf_api_secret.encode('utf-8'),
            payload_encoded.encode('utf-8'),
            _sha512)

        self.ws.send(dumps({'command': 'subscribe', 'channel': '1002'}))                            # Public Ticker Data - для monitoring pairs
        self.ws.send(dumps({'command': 'subscribe', 'channel': '1010'}))                            # Public Heartbeat

        self.ws.send(dumps({'command': 'subscribe',
                            'channel': '1000',
                            'sign': sign.hexdigest(),
                            'key': conf_api_key,
                            'payload': payload_encoded}))  # Private channel

        for pair in self.glob.data.rotatable_pair_ids:                                           # только ротационные пары
            self.ws.send(dumps({'command': 'subscribe', 'channel': pair}))                          # Pairs channel

    def close(self):
        self.ws.close()

    def reconnect(self):
        self.close()
        self.ws = self.start_socket_client()
        sleep(2)

    #   ###############################################################################################################
    #   ###############################################################################################################
    #   ##################################  interpreting stream message here  #########################################
    #   ###############################################################################################################
    #   ###############################################################################################################

    def msg_interpreter(self, msg):
        channel = int(msg[0])

        flag_processed = False              # сообщение было обработано, отдавать отчет в поток пары
        flag_run_strategy = False           # запустить одну итерацию стратегии
        # flag_graphics = False             # обновить графику

        flag_finish_sell_stage = False      # завершить всю сессию
        flag_finish_buy_stage = False       # завершить buy сессию, открыть sell

        _pair = ''

        #   #########################################  1002 channel  ##################################################

        if channel == 1002:
            # публичный канал тикера пар - мониторим только наши пары и только по 1002 обновляются курсы кросс пар!
            if msg[2][0] in self.glob.data.monitoring_pair_ids:
                self.log.socket(msg)
                _pair = self.glob.data.pair_by_id[msg[2][0]]
                _rate = float(msg[2][1])
                _ask = float(msg[2][2])
                _bid = float(msg[2][3])
                _day_change = round(float(msg[2][4]) * 100, 2)
                _day_volume_rated = float(msg[2][5])
                _day_volume_cur = float(msg[2][6])
                _is_frozen = int(msg[2][7])
                _day_high = float(msg[2][8])
                _day_low = float(msg[2][9])
                self.pairs.update_ticker_by_socket(_pair, _ask, _bid, _rate, _day_change, _day_volume_rated, _day_volume_cur, _is_frozen, _day_high, _day_low)

        #   ###########################  pairs channel / Price Aggregated Book ########################################

        elif channel in self.glob.data.rotatable_pair_ids:
            # публичный канал пар
            self.log.socket(msg)
            _pair = self.glob.data.pair_by_id[msg[0]]

            for _ in msg[2]:
                if _[0] == 'i':
                    lst = _[1]['orderBook']
                    tmp = [{}, {}]
                    for typ in [0, 1]:
                        for key, val in lst[typ].items():
                            tmp[typ][float(key)] = float(val)
                    # self.public_orders[_pair].public_orders_import(tmp)
                    flag_run_strategy = True
                    flag_processed = True

                elif _[0] == 'o':
                    _type = int(_[1])
                    _rate = float(_[2])
                    _amount = float(_[3])
                    # self.public_orders[_pair].public_orders_update(_type, _rate, _amount)
                    flag_processed = True

                elif _[0] == 't':
                    # ['t', '10301872', 1, '0.06216766', '149.83249203', 1627633826, '1627633826426']
                    _trade_id = int(_[1])
                    _type = int(_[2])
                    _rate = float(_[3])
                    _amount = float(_[4])
                    _time = int(_[5])
                    # self.pairs[_pair].update_rate_by_socket(_rate)  # дублирует обновление по 1002
                    # self.charts[_pair].update_by_socket(_rate, _amount)
                    # self.public_trades[_pair].add_public_trade_by_socket(_time, _trade_id, _type, _rate, _amount)
                    flag_run_strategy = True
                    flag_processed = True

                else:
                    self.log.error('Unknown message type in pairs channel {}'.format(msg))

        #   #########################################  1000 channel  ##################################################

        elif channel == 1000:  # канал 1000 приватные изменения / Account Notifications
            self.log.socket(msg)

            for _ in msg[2]:
                if _[0] == 'p':     # сообщение размещения отложенного ордера, полностью дублирует -n-
                    # ["p", <order number>, <currency pair id>, "<rate>", "<amount>", "<order type>", "<clientOrderId>"]
                    if conf_market_type == 'margin':
                        _order = int(_[1])
                        _pair = self.glob.data.pair_by_id[int(_[2])]
                        _rate = float(_[3])
                        _amount = float(_[4])
                        _type = conf_buy_sell[int(_[5])]
                        _coin = self.glob.data.coin_by_pair[_pair]
                        self.glob.add_order_params(_order, _pair, _type)  # сохраняем связь order - pair
                        # self.session.upd_session_socket_p(_order, _type, _rate, _amount)
                        # self.balances.upd_balance_by_sock_o_n(_pair, _coin, _amount, _type)  # устанавливаем 'onOrders'
                        flag_processed = True
                        if _order == self.glob.data.pair_wait_socket_msg[_pair]:
                            self.glob.pair_wait_socket_msg[_pair] = False

                elif _[0] == 'n':       # сообщение размещения ордера
                    if conf_market_type == 'exchange':
                        # ["n", <currency pair id>, <order number>, <order type>, "<rate>", "<amount>", "<date>", "<original amount ordered>" "<clientOrderId>"]
                        _pair = self.glob.data.pair_by_id[int(_[1])]
                        _coin = self.glob.data.coin_by_pair[_pair]
                        _order = int(_[2])
                        _type = conf_buy_sell[int(_[3])]
                        _rate = float(_[4])
                        _amount = float(_[5])
                        _date = int(mktime(strptime(_[6], '%Y-%m-%d %H:%M:%S')))
                        _amount_orig = float(_[7])
                        self.glob.add_order_params(_order, _pair, _type)   # сохраняем связь order - pair
                        # self.session.upd_session_socket_n(_order, _type, _rate, _amount, _date, _amount_orig)
                        # self.balances.upd_balance_by_sock_o_n(_pair, _coin, _amount, _type)     # устанавливаем 'onOrders'
                        flag_processed = True
                        if _order == self.glob.data.pair_wait_socket_msg[_pair]:
                            self.glob.data.pair_wait_socket_msg[_pair] = False

                elif _[0] == 'k':       # сообщение об уничтожении ордера
                    self.log.error(' -k- сообщение об уничтожении ордера, не обрабатывается !!!')

                elif _[0] == 'b':       # сообщение изменения баланса
                    _coin = self.coins.coin_by_id[int(_[1])]
                    _wallet = _[2]      # e (exchange), m (margin), or l (lending)
                    _balance_change = float(_[3])
                    # _pair = self.glob.base_coin_pair_by_coin(_coin)
                    # _rate = self.pairs[_pair].rate
                    self.balances.upd_balance_by_sock_b(_coin, _balance_change, _wallet)   # изменяем балансы валют
                    flag_run_strategy = True
                    flag_processed = True

                elif _[0] == 't':       # сообщение трейда
                    # ["t", <trade ID>, "<rate>", "<amount>", "<fee multiplier>", <funding type>, <order number>, <total fee>, <date>, "<clientOrderId>", "<trade total>"]
                    _trade_id = int(_[1])
                    _rate = float(_[2])
                    _amount = float(_[3])
                    _fee_rate = float(_[4])     # fee multiplier '0.00250000' of 0.25%)
                    _fund_type = int(_[5])
                    _order = int(_[6])
                    _pair = self.glob.pair_by_order(_order)
                    if _pair:
                        _fee = float(_[7])      # total fee is (amount * rate) * fee multiplier
                        _date = int(mktime(strptime(_[8], '%Y-%m-%d %H:%M:%S')))
                        _type = self.glob.type_by_order(_order)
                        _total = ro8(_amount * _rate)
                        _trade_total = float(_[10])
                        # self.session.upd_sess_trade_socket_t(_trade_id, _rate, _amount, _fee, _total, _type, _order, _date)
                        # self.private_trades.add_private_trade_by_socket(_trade_id, _rate, _amount, _fee, _total, _type, _order, _date)
                        flag_run_strategy = True
                        flag_processed = True
                    else:
                        if log_debug_socket_updates:
                            self.log.error('Unknown pair in private channel, ignoring "t" message')

                elif _[0] == 'o':       # сообщение обновления ордера
                    _order = int(_[1])
                    _pair = self.glob.pair_by_order(_order)
                    if _pair:
                        _type = self.glob.type_by_order(_order)
                        _coin = self.glob.data.coin_by_pair[_pair]
                        _amount = float(_[2])
                        _oper = _[3]     # f - filled order, c - cancelled order, s - filled self-trade order
                        # _rate = self.session.order_rate
                        # self.session.upd_sess_bal_socket_o(_order, _oper, _amount)    # устанавливаем amount сессии
                        self.balances.upd_balance_by_sock_o_n(_pair, _coin, _amount, _type)  # устанавливаем 'onOrders'
                        if _oper in ['f', 's'] and _amount == 0:
                            if _type in conf_buy_idx:
                                flag_finish_buy_stage = True    # закрываем покупку, переходим к продаже
                            else:
                                flag_finish_sell_stage = True   # полностью продали, закрываем сессию
                        flag_run_strategy = True
                        flag_processed = True
                        if _order == self.glob.data.pair_wait_socket_msg[_pair]:
                            self.glob.data.pair_wait_socket_msg[_pair] = False
                    else:
                        self.log.error('Unknown pair in private channel, ignoring "o" message')

                elif _[0] == 'm':   # сообщение обновление маржинального ордера
                    # ["m", <order number>, "<currency>", "<amount>", "<clientOrderId>"]
                    _order = int(_[1])
                    _coin = self.coins.coin_by_id[int(_[2])]
                    _amount = float(_[3])
                    _pair = self.coins.base_coin_pair_by_coin[_coin]
                    flag_processed = True
                    if _order == self.glob.data.pair_wait_socket_msg[_pair]:
                        self.glob.data.pair_wait_socket_msg[_pair] = False

                else:
                    self.log.error('Unknown private channel message type {}'.format(_))
        else:
            self.log.socket('Unknown channel: {}'.format(msg))

        # if flag_processed:
        #     if _pair in conf_pairs:
        #         self.pairs[_pair].rotation.append({
        #             'time': time(),
        #             'flag_run_strategy': flag_run_strategy,
        #             'flag_finish_buy_stage': flag_finish_buy_stage,
        #             'flag_finish_sell_stage': flag_finish_sell_stage
        #          })
