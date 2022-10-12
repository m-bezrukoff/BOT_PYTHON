conf_api_key = '5ZZ7L2T8-FDTCMW1E-12NLQKG9-7YM85NB1'
conf_api_secret = '1f856fdc14f72cd76f022a0ad0f3ba41b6caf8eace996dae915dc550d29a52496ed2610b724d57f5224862010e7044b5b8b45e85c003fb7ad5cc81e818b96616'
conf_market_fee = 0.125         # комиссия в % с операции

conf_market_type = 'margin'     # margin or exchange
# conf_market_type = 'exchange'     # margin or exchange

conf_allow_buy = 1              # разрешить buy
conf_allow_sell = 1             # разрешить sell
conf_rate_undercut = 1          # подрезать цену на 0.00000001 или ставить ордер в цену конкурента

debug_allow_strategy = 1        # разрешать работу стратегии пары
debug_auto_cancel_orders = 0    # запретить автоматическиое снятие ордеров при запуске (0 - только для дебага)
debug_buy_anyway = 0            # запускать покупку без сигнала score ( 1 - только для дебага)
debug_sell_anyway = 0           # запускать продажу без сигнала score ( 1 - только для дебага)

log_socket_save = 0             # сохраняет данные сокета в файл
log_pairs_save = 0              # сохраняет лог пар в файл


log_debug_socket_updates = 0
log_debug_strategy = 1
log_debug_sessions = 1

conf_total_candles = 310        # Общее количество запрашиваемых свечей каждого таймфрейма (с запасом из-за графика)
conf_display_candles = 288      # Количество свечей, отображаемых на графике
conf_public_trades_limit = 180  # Количество дней, хранимых в базе

conf_buy_cancel = 0.2           # предел роста цены в % от сигнала на вход, после которого покупка уже не интересна
conf_buy_trigger = 0.00         # порог роста цены в % от минимума, покупаем!
conf_stop_loss = -1.2           # предел падения цены в % от уровня открытия сессии - срочно продаем
conf_sell_trigger = 0           # порог падения цены в % от максимума, продаем!

conf_request_delay = 0.001      # в Poloniex уже зашит в API задержка в сек между запросами к бирже 6 запросов в сек
conf_pairs_rotation_delay = 0.9       # задержка в сек ротации пары
conf_graph_rotation_delay = 0.9       # задержка в сек ротации пары

conf_base_coin = 'USDT'         # базовая валюта

conf_pairs = {
    # 'USDT_ETH': {'cluster': {'5m': 40, '15m': 35, '30m': 30}},
    'USDT_BTC': {'cluster': {'5m': 40}},
    # 'USDT_BTC': {'cluster': {'5m': 25, '15m': 20, '30m': 15}},
    # 'USDT_JST',
    # 'USDT_USDJ',
    # 'USDT_TRX': {'cluster': {'5m': 40, '15m': 35, '30m': 30}},
    # 'USDT_XRP',
    # 'USDT_COMP',
    # 'USDT_BULL',
    # 'USDT_JST',
    # 'BTC_ETH',
    # 'BTC_XRP',
    # 'BTC_LTC',
    # 'BTC_XMR',
    # 'BTC_AVA',
    # 'BTC_STR',
    # 'USDT_BEAR': {'cluster': {'5m': 40, '15m': 35, '30m': 30}},
    # 'BTC_BNT',
}

conf_time_frames = {'5m': 300}         # используемые таймфреймы 5m, 30m, 2h
# conf_time_frames = {'5m': 300, '15m': 900, '30m': 1800}         # используемые таймфреймы 5m, 30m, 2h

conf_trade_bounds = {
    'USDT': {'market_bound': 1, 'amount_limit': 1.1},           # базовый максимальный объем покупок USD
    'BTC': {'market_bound': 0.0001, 'amount_limit': 0.00012},   # базовый максимальный объем покупок BTC
}

conf_sell_idx = (0, '0', 'sell', 'asks')
conf_buy_idx = (1, '1', 'buy', 'bids')
conf_buy_sell = {1: 'buy', 0: 'sell', 'buy': 1, 'sell': 0}
conf_asks_bids = {1: 'bids', 0: 'asks', 'bids': 1, 'asks': 0}

conf_tools_clusters = True      # использование кластерного анализа
