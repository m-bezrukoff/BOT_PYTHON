from inc.inc_functions import percent, add_percent, weighted_average

class Session:
    def __init__(self):
        self.trades = []
        self.positions = {}
        self.orders = self.set_initial_orders()
        self.first_lot_amount = 1
        self.average_lot_price = 0

        self.net_range = {'min': 45000, 'max': 47600, 'mid': (45000 + 47600) / 2}
        self.net_step = 0.1     # percent
        self.net_segments_count = percent(self.net_range['min'], self.net_range['max']) / self.net_step
        print('*************************', self.net_segments_count)
        self.net_orders = {}

    # def add_trade(self, amount, price, typ, date):
    #     self.trades.append((amount, price, typ, date))
    #
    # def add_trade(self, amount, price, typ, date):
    #     self.trades.append((amount, price, typ, date))
    #
    # def calc_average_lot_price(self):
    #     self.average_lot_price = sum(list_rate[i] * list_amount[i] / sum(list_amount) for i in range(len(list_rate)))
    #
    # def set_initial_orders(self):
    #     orders = {}
    #     return orders
    #
    # def run_net(self):
