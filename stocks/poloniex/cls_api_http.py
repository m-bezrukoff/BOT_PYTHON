from config import *
from stocks.poloniex.poloniex_api import Poloniex
from inc.inc_system import find_candle_start_by_candles_ago, sleep, utc_date_to_timestamp, time
from classes.cls_api_queue import ApiQueue
from classes.cls_dataclasses import PublicTradeData


class ApiPoloniex:
    def __init__(self, glob, log):
        super().__init__()
        self.log = log
        self.glob = glob
        self.deco = ApiQueue(log)
        self.request_timestamp = time() - 10
        self.balances_request_time = time() - 10
        self.balances_cache = ''
        self.orders_request_time = time() - 10
        self.orders_cache = ''
        self.count = 0
        self.rest_api = Poloniex(conf_api_key, conf_api_secret)
        self.buy_sell_mapping = {'buy': 1, 'sell': 0}

    # -------------------------------------- get_balances -> returnCompleteBalances ------------------------------------

    @ApiQueue.checkin
    def api_return_complete_balances(self):
        try:
            res = self.rest_api.returnCompleteBalances('all')
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnCompleteBalances -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(10)
                self.api_return_complete_balances()

    # ---------------------------------- get_balances -> returnAvailableAccountBalances --------------------------------

    @ApiQueue.checkin
    def get_available_account_balances(self):
        try:
            res = self.rest_api.returnAvailableAccountBalances()
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnAvailableAccountBalances -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(10)
                self.get_available_account_balances()

    # -------------------------------------- get_balances -> returnBalances ---------------------------------------

    @ApiQueue.checkin
    def api_return_balances(self):
        try:
            res = self.rest_api.returnBalances()
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnBalances -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(10)
                self.api_return_balances()

# --------------------------------------- get_orders -> returnOpenOrders ---------------------------------------------

    @ApiQueue.checkin
    def get_orders(self):
        try:
            res = self.rest_api.returnOpenOrders()
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnOpenOrders -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# ---------------------------------------------- returnCurrencies -----------------------------------------------------

    @ApiQueue.checkin
    def get_coins(self):
        # returnCurrencies
        try:
            res = self.rest_api.returnCurrencies()
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            if err:
                self.glob.data['stop_by']['requests'] = True
                self.log.requests(f'returnCurrencies error -> {str(err)}')
                self.log.error(f'returnCurrencies error -> {str(err)}')
                if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                    sleep(5)

# ----------------------------------- update_from_ticker -> returnTicker ----------------------------------------------

    @ApiQueue.checkin
    def get_ticker(self):
        # returnTicker
        try:
            res = self.rest_api.returnTicker()
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnTicker -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# ------------------------------------------ get_chart -> returnChartData  --------------------------------------------

    @ApiQueue.checkin
    def get_chart(self, pair, candles, frame):
        # returnChartData
        try:
            self.request_timestamp = time()
            frame = conf_time_frames[frame]
            start = find_candle_start_by_candles_ago(candles, frame)
            res = self.rest_api.returnChartData(pair, frame, start, end=9999999999)
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnChartData {pair} -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# ----------------------------------- get_trades_public -> marketTradeHist --------------------------------------------

    @ApiQueue.checkin
    def get_trades_public(self, pair: str, start: int = None, end: int = None) -> list[PublicTradeData]:
        """ marketTradeHist Returns the past 200 trades for a given market, or up to 1,000 trades
            between a range specified in UNIX timestamps by the "start" and "end" GET parameters.
            {"globalTradeID": 495739474, "tradeID": 38444414, "date": "2020-11-07 20:48:00", "type": "sell",
            "rate": "14826.63873565", "amount": "0.00006913", "total": "1.02496553", "orderNumber": 779496208636},
        """
        try:
            res = self.rest_api.returnTradeHistoryPublic(pair, int(start), int(end))
            self.glob.data['stop_by']['requests'] = False

            return [PublicTradeData(
                utc_date_to_timestamp(i['date']),
                int(i['tradeID']),
                self.buy_sell_mapping[i['type']],
                float(i['rate']),
                float(i['amount'])
            ) for i in res]

        except Exception as e:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'marketTradeHist error -> {str(e)}')
            if 'HTTPError' in str(e) or 'ConnectionError' in str(e):
                sleep(5)

# ----------------------------------- get_trades_private -> returnTradeHistory (private) ------------------------------

    @ApiQueue.checkin
    def get_trades_private(self, pair='all', fr=None, to=None, lim=10000):
        # returnTradeHistory
        try:
            res = self.rest_api.returnTradeHistory(currencyPair=pair, start=fr, end=to, limit=lim)
            self.glob.data['stop_by']['requests'] = False
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'returnTradeHistory private error -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# ----------------------------------------- cancel_order -> cancelOrder -----------------------------------------------

    @ApiQueue.checkin
    def cancel_order(self, num, pair):
        # cancelOrder
        try:
            res = self.rest_api.cancelOrder(num)
            self.glob.data['stop_by']['requests'] = False
            self.glob.data['pair_wait_socket_msg'][pair] = num  # флаг ожидания сообщения по сокету при следующей итерации
            return res
        except Exception as err:
            self.glob.data['stop_by']['requests'] = True
            self.log.requests(f'cancelOrder error -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# ------------------------------------- cancel_all_orders -> cancelAllOrders ------------------------------------------

    # @ApiQueue.queuer
    # def cancel_all_orders(self, pair):
    #     # cancelAllOrders
    #     try:
    #         res = self.rest_api.cancelAllOrders(pair)
    #         self.glob.data['stop_by']['requests'] = False
    #         return res
    #     except Exception as err:
    #         self.glob.data['stop_by']['requests'] = True
    #         self.log.requests(f'{0} cancelAllOrders error -> {str(err)}')
    #         if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
    #             sleep(5)

# --------------------------------------------- buy  for exchange market -----------------------------------------------

    @ApiQueue.checkin
    def buy(self, pair, rate, amount):
        try:
            res = self.rest_api.buy(pair, rate, amount, postOnly=1)
            self.glob.data['stop_by']['requests'] = False
            if res:
                self.glob.data['pair_wait_socket_msg'][pair] = res['orderNumber']  # ожидаем сообщение об ордере по сокету, только после этого итерация
                self.glob.add_order_params(res['orderNumber'], pair, 'buy')     # для устранения рассинхрона привязки
            return res
        except Exception as err:
            if 'Total must be at least' in str(err):
                self.log.requests(f'buy error -> {str(err)}')
            elif 'Unable to place post-only order at this price' in str(err):
                self.log.requests(f'buy error -> {str(err)}')
                self.log.log(f'{pair} buy error -> {str(err)}')
            else:
                self.glob.data['stop_by']['requests'] = True
                self.log.requests(f'buy error -> {str(err)}')
                if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                    sleep(5)

# -------------------------------------- sell  for exchange market -----------------------------------------------------

    @ApiQueue.checkin
    def sell(self, pair, rate, amount):
        try:
            res = self.rest_api.sell(pair, rate, amount)
            self.glob.data['stop_by']['requests'] = False
            if res:
                self.glob.data['pair_wait_socket_msg'][pair] = res['orderNumber']  # ожидаем сообщение об ордере по сокету, только после этого итерация
                self.glob.add_order_params(res['orderNumber'], pair, 'sell')     # для устранения рассинхрона привязки
            return res
        except Exception as err:
            if 'Total must be at least' in str(err):
                self.log.requests(f'sell error -> {str(err)}')
                self.log.log(f'{pair} sell error -> {str(err)}')
            else:
                self.glob.data['stop_by']['requests'] = True
                self.log.requests(f'sell error -> {str(err)}')
                if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                    sleep(5)

# ------------------------------------------------ moveOrder ----------------------------------------------------------

    @ApiQueue.checkin
    def move(self, order, rate, pair, post_only=1, amount=None):
        # moveOrder ТОЛЬКО ДЛЯ EXCHANGE РЫНКА !
        try:
            res = self.rest_api.moveOrder(order, rate, amount, post_only)
            self.glob.data['stop_by']['requests'] = False
            if res['success']:
                self.glob.data['pair_wait_socket_msg'][pair] = res['orderNumber']  # ожидаем сообщение об ордере по сокету, только после этого итерация
                self.glob.add_order_params(res['orderNumber'], pair, self.glob.type_by_order(order))    # для устранения рассинхрона привязки
            return res
        except Exception as err:
            if 'Total must be at least 0.0001' in str(err):
                self.log.requests(f'{pair} moveOrder error -> {str(err)} {rate}')
                self.log.log(f'{pair} moveOrder error -> {str(err)} {rate}')
            elif 'Unable to place post-only order at this price' in str(err):
                self.log.requests(f'{pair} moveOrder error -> {str(err)} {rate}')
                self.log.log(f'{pair} moveOrder error -> {str(err)} {rate}')
            elif 'is either completed or does not exist' in str(err):
                self.log.requests(f'moveOrder error -> {str(err)}')
                self.log.log(f'{pair} moveOrder error -> {str(err)} {rate}')
            elif 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                self.glob.data['stop_by']['requests'] = True
                sleep(5)
            else:
                self.log.requests(f'moveOrder other error -> {str(err)}')

# ---------------------------------- returnMarginAccountSummary --------------------------------------------------------

    @ApiQueue.checkin
    def get_margin_summary(self):
        try:
            res = self.rest_api.returnMarginAccountSummary()
            self.glob.data['stop_by']['requests'] = False
            if res:
                return res
            return False
        except Exception as err:
            self.log.requests(f'returnMarginAccountSummary error -> {str(err)}')
            self.log.error(f'returnMarginAccountSummary error -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# ------------------------------------------- getMarginPosition -------------------------------------------------------

    @ApiQueue.checkin
    def get_margin_position(self, pair):
        try:
            res = self.rest_api.getMarginPosition(pair)
            self.glob.data['stop_by']['requests'] = False
            if res:
                return res
            return False
        except Exception as err:
            self.log.requests(f'getMarginPosition error -> {str(err)}')
            self.log.error(f'getMarginPosition error -> {str(err)}')
            if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                sleep(5)

# -------------------------------- marginBuy    buy for margin market --------------------------------------------------

    @ApiQueue.checkin
    def margin_buy(self, pair, rate, amount):
        try:
            res = self.rest_api.marginBuy(pair, rate, amount, lendingRate=0.01)
            self.glob.data['stop_by']['requests'] = False
            if res:
                self.glob.data['pair_wait_socket_msg'][pair] = res['orderNumber']       # ожидаем сообщение об ордере по сокету, только после этого итерация
                self.glob.add_order_params(res['orderNumber'], pair, 'buy')     # для устранения рассинхрона привязки
            return res
        except Exception as err:
            if 'Total must be at least' in str(err):
                self.log.requests(f'margin_buy error -> {str(err)}')
            elif 'Unable to place post-only order at this price' in str(err):
                self.log.requests(f'margin_buy error -> {str(err)}')
                self.log.log(f'{pair} margin_buy error -> {str(err)}')
            else:
                self.glob.data['stop_by']['requests'] = True
                self.log.requests(f'margin_buy error -> {str(err)}')
                if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                    sleep(5)

# ----------------------------------- sell    sell for margin market ---------------------------------------------------

    @ApiQueue.checkin
    def margin_sell(self, pair, rate, amount):
        try:
            res = self.rest_api.marginSell(pair, rate, amount, lendingRate=0.01)
            self.glob.data['stop_by']['requests'] = False
            if res:
                self.glob.data['pair_wait_socket_msg'][pair] = res['orderNumber']       # ожидаем сообщение об ордере по сокету, только после этого итерация
                self.glob.add_order_params(res['orderNumber'], pair, 'sell')            # для устранения рассинхрона привязки
            return res
        except Exception as err:
            if 'Total must be at least' in str(err):
                self.log.requests(f'margin_sell error -> {str(err)}')
                self.log.log(f'{pair} margin_sell error -> {str(err)}')
            else:
                self.glob.data['stop_by']['requests'] = True
                self.log.requests(f'margin_sell error -> {str(err)}')
                if 'HTTPError' in str(err) or 'ConnectionError' in str(err):
                    sleep(5)
