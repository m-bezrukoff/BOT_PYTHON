from config import *
from time import mktime, strptime


class OrdersPrivate:
    def __init__(self, pair, api):
        self.pair = pair
        self.glob = api.glob
        self.api = api
        self.log = api.log
        self.data = {}
        self.is_updated = False

    def cancel_private_order(self, order_id):
        res = self.api.cancel_order(order_id, self.pair)
        if res:
            if res['success']:
                self.glob.pair_wait_socket_msg[self.pair] = order_id    # ожидаем сообщение об ордере по сокету, только после этого итерация
                try:
                    _ = self.data.pop(order_id)
                    self.glob.mark_order_params_to_delete([order_id])
                except KeyError:
                    self.log.log(self.pair, 'cancel_order {} not found in orders or glob'.format(order_id))
                self.log.log(self.pair, 'Order {} cancelled'.format(order_id))
            else:
                self.log.log(self.pair, 'Order {} NOT cancelled! {}'.format(order_id, res['message']))

    def cancel_all_private_orders(self):
        if self.data:
            for _ in list(self.data.keys()):
                self.cancel_private_order(_)

    def add_private_orders(self, lst):
        if lst:
            for _ in lst:
                self.add_private_order(_)

    def add_private_order(self, dic):
        if (int(dic['orderNumber'])) not in self.data:
            order = int(dic['orderNumber'])
            typ = conf_buy_sell[dic['type']]
            self.data[order] = {
                'type': int(typ),
                'rate': float(dic['rate']),
                'startingAmount': float(dic['startingAmount']),
                'amount': float(dic['amount']),
                'total': float(dic['total']),
                'date': int(mktime(strptime(dic['date'], '%Y-%m-%d %H:%M:%S'))),
                'margin': float(dic['margin'])}
            self.glob.add_order_params(order, self.pair, typ)
