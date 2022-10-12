from inc.inc_system import to8


class OrdersPublic:     # ex OrderBook
    def __init__(self, pair, pairs):
        # self.pair = pair
        self.pairs = pairs[pair]
        self.log = pairs[pair].log
        self.data = [{}, {}]  # 0: 'sell', 1: 'buy'

    def public_orders_update(self, typ, rate, amount):
        try:
            if amount:
                self.data[typ][rate] = amount
            else:
                self.data[typ].pop(rate)
            self.update_pair_bids_asks()
        except IndexError:
            pass

    def public_orders_import(self, lst):
        self.data = lst   # очищаем прежние значения, импорт может быть повторным
        self.update_pair_bids_asks()

    def update_pair_bids_asks(self):
        lst = sorted(self.data[0].keys())
        self.pairs.ask_rate = lst[0]
        self.pairs.ask_amount = self.data[0][lst[0]]
        self.pairs.ask_2nd_rate = lst[1]
        self.pairs.ask_2nd_amount = self.data[0][lst[1]]
        # print('ask:', to8(self.pairs.ask_rate), to8(self.pairs.ask_amount), to8(self.pairs.ask_2nd_rate), to8(self.pairs.ask_2nd_amount))

        lst = sorted(self.data[1].keys(), reverse=True)
        self.pairs.bid_rate = lst[0]
        self.pairs.bid_amount = self.data[1][lst[0]]
        self.pairs.bid_2nd_rate = lst[1]
        self.pairs.bid_2nd_amount = self.data[1][lst[1]]
        # print('bid:', to8(self.pairs.bid_rate), to8(self.pairs.bid_amount), to8(self.pairs.bid_2nd_rate), to8(self.pairs.bid_2nd_amount))
