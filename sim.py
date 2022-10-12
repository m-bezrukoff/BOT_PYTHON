from simulator.sim.sim_config import *
from simulator.sim.cls_sim_pairs import *
from classes.cls_globals import Globals
from classes.cls_pairs import Pairs
from classes.cls_socket_server import SocketServer
from classes.cls_indicators import Indicators
from classes.cls_pairs_thread import ExchangeThread
from pprint import pprint
from inc.inc_system import sleep, time,  utc_timestamp_to_date, local_timestamp_to_date, find_candle_start_time, to8

if __name__ == "__main__":

    pair = 'USDT_TRX'

    log = SimLog()
    glob = Globals()

    api = SimApi(glob, log)
    public_trades = {pair: SimPublicTrades(pair, api, log) for pair in conf_pairs}
    start_timestamp = public_trades[pair].data[0]['timestamp']

    private_trades = {pair: SimPrivateTrades(pair, api, log) for pair in conf_pairs}
    charts = {pair: SimCharts(pair, api, glob, log) for pair in conf_pairs}
    pairs = {pair: Pairs(pair, 1, glob, charts, log) for pair in conf_pairs}
    socket_server = SocketServer(glob, log)
    socket_server.start()
    indicators = {pair: SimIndicators(pair, pairs, charts, public_trades, private_trades, socket_server) for pair in conf_pairs}

    balances = Balances()
    session = SimSession()

    public_orders = {pair: object for pair in conf_pairs}
    coins = object
    private_orders = {pair: object for pair in conf_pairs}
    sessions = {pair: object for pair in conf_pairs}
    thread_pairs = {pair: SimExchangeThread(pair, glob, pairs, charts, session, indicators) for pair in conf_pairs}



    # запускаем перебор трейдов
    # t1 = time()
    # for i in public_trades[pair].data[:1000]:
    #     # print(i)
    #     charts[pair].update_by_sim(i['date'], i['rate'], i['amount'], i['type'])
    #     # print(charts[pair].data['5m'][-1])
    #     try:
    #         indicators[pair].update_indicators()
    #     except Exception as e:
    #         pass

        # thread_pairs[pair].market_type_selector()
    # print('time spent:', time() - t1)

    # for i in range(100):
    #     indicators[pair].sim_export_graphics_data(pair)
    print(utc_timestamp_to_date(public_trades[pair].data[0]['date']))
    print('...')
    print(utc_timestamp_to_date(public_trades[pair].data[-1]['date']))

    print(charts[pair].data['5m'][0])
    print('...')
    print(charts[pair].data['5m'][-1])






