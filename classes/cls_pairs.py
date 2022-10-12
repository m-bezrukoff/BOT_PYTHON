from config import *
# from inc.inc_system import to8, time
from stocks.poloniex.poloniex_functions import update_ticker


class Pairs:

    def __init__(self, glob, log, shared, preload):
        self.data = shared.dict()
        self.log = log

        for pair in glob.data.monitoring_pairs:
            self.data[pair] = shared.Namespace()
            self.data[pair].id = glob.data.id_by_pair[pair]
            self.data[pair].is_rotatable = True if pair in conf_pairs else False
            self.data[pair].rate = 0

            self.data[pair].coin = pair.split('_')[1] if pair.split('_')[0] == conf_base_coin else pair.split('_')[0]
            self.data[pair].is_updated_by_ticker = False
            self.data[pair].is_frozen = False
            self.data[pair].is_ready = False
            self.data[pair].day_change = 0
            self.data[pair].day_volume_rated = 0
            self.data[pair].day_volume_cur = 0
            self.data[pair].day_high_rate = 0
            self.data[pair].day_low_rate = 0
            self.data[pair].ask_rate = 0  # курс предложения
            self.data[pair].ask_amount = 0
            self.data[pair].bid_rate = 0  # курс спроса
            self.data[pair].bid_amount = 0

            # self.market_bound = conf_trade_bounds[conf_base_coin]['market_bound']
            # self.amount_limit = conf_trade_bounds[conf_base_coin]['amount_limit']

            self.initial_upgate_by_preload(pair, preload.data['ticker'][pair])

    def update_ticker_by_socket(self, pair, ask, bid, rate, day_change, day_volume_rated, day_volume_cur, is_frozen, day_high, day_low):
        self.data[pair].rate = rate
        self.data[pair].ask_rate = ask
        self.data[pair].bid_rate = bid
        self.data[pair].day_change = day_change
        self.data[pair].day_volume_rated = day_volume_rated
        self.data[pair].day_volume_cur = day_volume_cur
        self.data[pair].is_frozen = is_frozen
        self.data[pair].day_high_rate = day_high
        self.data[pair].day_low_rate = day_low
        self.data[pair].is_updated_by_ticker = True

    def initial_upgate_by_preload(self, pair, data):
        res = update_ticker(data)
        for i in res:
            setattr(self.data[pair], i, res[i])
