from config import *
from sys import argv, exit
from multiprocessing import Manager
from classes.cls_globals import Globals
from classes.cls_log import Log
from PyQt6.QtWidgets import QApplication
from classes.cls_app import App
from classes.cls_time_sync import TimeSync
from classes.cls_pipe import MyPipe
from classes.cls_api import Api
from classes.cls_communicator import ProcessCommunicator
from classes.cls_preload import Preload
from classes.cls_coins import Coins
from classes.cls_balances import Balances
from classes.cls_pairs_multiprocessing import PairsMultiprocessing, Lock
from stocks.poloniex.cls_api_socket import ApiSocket
from classes.cls_pairs import Pairs
from classes.cls_orders_public import OrdersPublic
# from classes.cls_trades_public import TradesPublic
# from classes.cls_trades_public_clusters import Clusters
# from classes.cls_charts import Charts
# from classes.cls_indicators import Indicators
# from classes.cls_session import Sessions
# from classes.cls_orders_private import OrdersPrivate
# from classes.cls_trades_private import PrivateTrades
# from classes.cls_socket_server import SocketServer
# from classes.cls_service_thread import ServiceThread
from classes.cls_dataclasses import SendApiMsg, ReceiveApiMsg, ReceiveMsg
from time import sleep
from pprint import pprint

if __name__ == "__main__":
    shared = Manager()
    pipe_log = MyPipe()
    pipe_api = MyPipe()
    pipe_socket = MyPipe()
    pipe_main = MyPipe()
    lock = Lock()

    glob = Globals(shared)
    log = Log(pipe_log)

    pipe_pair = {pair: MyPipe() for pair in conf_pairs}     # ВНИМАНИЕ на обрабатываемые пары!

    app = QApplication(argv + ['--disable-logging'])
    window = App(glob, log, pipe_pair, pipe_log, pipe_api, pipe_socket)
    window.show()
    time_sync = TimeSync(glob, log)
    api = Api(glob, log, lock, pipe_pair, pipe_api, pipe_main)
    preload = Preload(glob, log, pipe_api, pipe_main)

    coins = Coins(glob, log, preload)
    balances = Balances(glob, log, shared, coins, preload)
    pairs = Pairs(glob, log, shared, preload)
    api_socket = ApiSocket(glob, log, api, coins, balances, pairs)
    pair_processes = PairsMultiprocessing(glob, log, lock, pipe_pair, pipe_main, pipe_log, pairs, balances)

    app.api_socket = api_socket
    exit(app.exec())

    # communicator = ProcessCommunicator(lock, pipe_api, pipe_socket, pipe_main, log)
    # SendApiMsg(pipe_api, 'get_ticker', 'pipe_main')

    # sleep(5)
    # for i in range(20):
    #     sleep(0.5)
    #     print('sending', i)
    #     pipe_pair['USDT_TRX'].a.send(i)

    # socket_server = SocketServer(glob, log)
    # public_trades = {pair: TradesPublic(pair, log, api) for pair in conf_pairs}
    # clusters = {pair: Clusters(pair, public_trades[pair]) for pair in conf_pairs}
    # private_orders = {pair: OrdersPrivate(pair, api) for pair in conf_pairs}
    # private_trades = {pair: PrivateTrades(pair, api, log) for pair in conf_pairs}
    # charts = {pair: Charts(pair, api) for pair in conf_pairs}
    # public_orders = {pair: OrdersPublic(pair, pairs) for pair in conf_pairs}
    # session = Sessions(private_trades, private_orders, pairs, charts, glob, coins, log)

    # indicators = {pair: Indicators(pair, pairs, charts, public_trades, private_trades, socket_server) for pair in conf_pairs}
    # thread_service = ServiceThread(glob, api, pairs, public_orders, public_trades, charts, coins, balances, private_orders, private_trades, log, thread_socket)

    # socket_server.start()
    # thread_socket.start()
    # thread_service.start()
    # for pair in conf_pairs:
    #     thread_pairs[pair].start()
