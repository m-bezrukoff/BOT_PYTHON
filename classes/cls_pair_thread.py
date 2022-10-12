from classes.exchange.cls_exchange_strategy import ExchangeStrategy
from classes.margin.cls_margin_strategy import MarginStrategy
from config import *
from inc.inc_system import to8, sleep, time
from PyQt6.QtCore import QThread
from classes.cls_log import Log
from classes.cls_log_in_process import LogInsideProcess
from classes.cls_dataclasses import SendMsg, SendApiMsg, ReceiveMsg
from classes.cls_balances_proc import BalancesOfProcess


# class ExchangeThread(ExchangeStrategy, MarginStrategy, QThread):
class PairThread:
    def __init__(self, pair, glob_data, lock, pipe_pair, pipe_main, pipe_log, pairs_data, current_pair_data, balances_data):
        super().__init__()
        self.pair = pair
        self.lock = lock
        self.glob = glob_data
        self.pipe_pair = pipe_pair
        self.pipe_main = pipe_main
        self.pairs_tickers = pairs_data
        self.ticker = current_pair_data
        self.log = LogInsideProcess(pipe_log, pair)
        self.lock.acquire()
        print('PairThread object created', self.pair)
        self.lock.release()
        self.run()

        # self.api = api
        # self.coins = coins
        self.balances = BalancesOfProcess(balances_data)

        # self.public_orders = public_orders[pair]
        # self.public_trades = public_trades[pair]
        # self.charts = charts[pair]
        # self.private_orders = private_orders[pair]
        # self.private_trades = private_trades[pair]
        # self.session = session
        # self.indicators = indicators[pair]
        # self.terminate_thread = False
        # self.execution_time = time()

    # def ready_check_initial(self):
    #     if not self.pairs.is_ready:
    #         while True:
    #             sleep(1)
    #             if self.pairs.is_updated_by_ticker:
    #                 if self.pairs.is_frozen == 0:
    #                     if self.pairs.ask_rate and self.pairs.bid_rate:
    #                         if self.private_orders.is_updated:
    #                             if self.balances.is_balances_updated:
    #                                 if self.coins.is_coins_updated:
    #                                     if self.charts.data['5m']:
    #                                         if self.public_trades.is_updated:
    #                                             if self.private_trades.is_updated:
    #                                                 self.log.log(self.pair, 'ready_check -> Pair thread is ready')
    #                                                 self.pairs.is_ready = True
    #                                                 break
    #                                             else:
    #                                                 self.log.log(self.pair, 'ready_check -> Private trades not ready!')
    #                                         else:
    #                                             self.log.log(self.pair, 'ready_check -> Public trades not ready!')
    #                                     else:
    #                                         self.log.log(self.pair, 'ready_check -> Charts not ready')
    #                                 else:
    #                                     self.log.log(self.pair, 'ready_check -> Coins not ready')
    #                             else:
    #                                 self.log.log(self.pair, 'ready_check -> Balances not ready')
    #                         else:
    #                             self.log.log(self.pair, 'ready_check -> Private orders not ready')
    #                     else:
    #                         self.log.log(self.pair, 'ready_check -> ask_rate or bid_rate not ready')
    #                 else:
    #                     self.log.log(self.pair, '{:-^80}'.format(' Frozen pair, canceling! '))
    #                     self.terminate_thread = True
    #             else:
    #                 self.log.log(self.pair, '{:-^80}'.format('ready_check -> Ticker not ready'))
    #
    # def ready_check_every_step(self):
    #     if self.glob.stop_by['socket']:
    #         self.log.log(self.pair, '{:-^80}'.format('Stop tactic by socket problem!'))
    #         sleep(1)
    #         return False
    #
    #     if self.glob.stop_by['requests']:
    #         self.log.log(self.pair, '{:-^80}'.format('Stop tactic by requests problem!'))
    #         sleep(1)
    #         return False
    #
    #     if self.glob.stop_by['charts']:
    #         self.log.log(self.pair, '{:-^80}'.format('Stop tactic by charts!'))
    #         sleep(1)
    #         return False
    #
    #     if self.glob.stop_by['closeApp']:
    #         self.terminate_thread = True
    #         return False
    #
    #     return True
    #
    # def market_type_selector(self):
    #     if self.ready_check_every_step():  # работа тактики только при работе сокетов и корректности чартов
    #         if debug_allow_strategy:
    #             self.log.log(self.pair, '-' * 40)
    #             if conf_market_type == 'exchange':
    #                 self.exchange_strategy_detector()
    #             elif conf_market_type == 'margin':
    #                 self.margin_strategy_detector()
    #             else:
    #                 self.log.log(self.pair, 'UNKNOWN MARKET TYPE')
    #         else:
    #             self.log.log(self.pair, 'Strategy disabled by debug_allow_strategy'.format(self.pair))
    #             sleep(1)
    #
    # def iteration_conditions(self):
    #     #   условия запуска итерации пары по очереди pairs.rotation сигналов сокета
    #     #   необходимо дождаться ответа на действия buy, sell, move, cancel
    #     if not self.glob.pair_wait_socket_msg[self.pair]:
    #         res = {'flag_finish_buy_stage': False, 'flag_finish_sell_stage': False}
    #         for i in range(len(self.pairs.rotation)):
    #             x = self.pairs.rotation.pop(0)
    #             if x['flag_finish_buy_stage']:
    #                 res['flag_finish_buy_stage'] = True
    #             if x['flag_finish_sell_stage']:
    #                 res['flag_finish_sell_stage'] = True
    #         return res
    #     return False
    #
    # # ################################################ pair cycle ######################################################
    #

    def run(self):
    #     self.log.log(self.pair, 'Updating charts')
    #     # self.charts.update_public_trades_by_request(conf_total_candles)   # initial charts
    #     self.public_trades.initialize()
    #     self.private_trades.private_trades_initial_update()
    #     self.indicators.update_indicators()
    #     self.ready_check_initial()
    #     if debug_auto_cancel_orders:
    #         self.private_orders.cancel_all_private_orders()
    #     # self.sessions.check_initial_session_relevance()     # проверяем корректность сессии при первом запуске
    #     self.log.log(self.pair, '{:-^80}'.format('PAIR STRATEGY STARTED'))
    #
        while True:
            # msg = ReceiveMsg(self.pipe_pair)
            # if msg.action == 'exit':
            #     print('closing', self.pair, 'thread')
            #     break
            self.log.log(f'rate {self.pair} : {self.pairs_tickers[self.pair].rate} {self.ticker.rate}')
            sleep(1)

    #         if self.terminate_thread:
    #             break
    #         if self.pairs.rotation:
    #             # try:
    #             rule = self.iteration_conditions()
    #
    #             if rule['flag_finish_buy_stage']:
    #                 self.session.finish_buy_stage()
    #                 self.session.save_session()
    #
    #             if rule['flag_finish_sell_stage']:
    #                 self.session.finish_sell_stage()
    #                 self.session.save_session()
    #
    #             # self.public_trades.pt_consistency()
    #             self.indicators.update_indicators()
    #             self.charts.check_charts_relevance_all_frames()
    #             self.market_type_selector()
    #             self.indicators.export_graphics_data()  # отправка через сокет данных на js график
    #             sleep(conf_pairs_rotation_delay)        # ограничиваем кол-во срабатываний в сек
    #
    #             # except Exception as err:
    #             #     self.log.log(self.pair, '{0} THREAD ERROR {0}'.format('-' * 40, self.pair))
    #             #     self.log.log(self.pair, err.__repr__())
    #             #     self.log.error_trace(self.pair, err)
    #         else:
    #             sleep(0.01)
    #
    #     self.log.log(self.pair, 'Thread {} finished'.format(self.pair))
