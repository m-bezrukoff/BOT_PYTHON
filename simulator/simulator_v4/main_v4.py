from simulator_data import Data
from inc.inc_functions import *


class Session:
    def __init__(self, _rate, _deep, _step):
        self.pnl = None
        self.rate = _rate
        self.step = _step
        self.zero_rate = _rate
        self.prev_rate = _rate
        self.init_rate = _rate   # курс нулевой отметки сетки
        self.deep = _deep
        self.is_active = False
        self.current_step = 0   # текущий пересеченный уровень сетки
        self.orders_buy = self.gen_orders('buy', _deep)     # ниже уровня
        self.orders_sell = self.gen_orders('sell', _deep)   # выше уровня
        self.position = []
        self.max_reached_level = 0

    @property
    def rate_opposite(self):
        weight_averate = sum([i['rate'] * i['amount'] for i in self.position]) / sum([i['amount'] for i in self.position])
        # print('rate_opposite', weight_averate)
        offset = self.step if self.position[0]['type'] == 'long' else -self.step
        # print('amount_opposite offset', offset)
        if len(set(([i['type'] for i in self.position]))) != 1:
            print(RED, 'в позиции есть разные направления!', END)
        return weight_averate + offset

    @property
    def amount_opposite(self):
        return sum([i['amount'] for i in self.position])

    @property
    def rate_full_diff(self):
        return percent(self.zero_rate, self.rate, accuracy=3)

    @property
    def rate_diff(self):
        return percent(self.prev_rate, self.rate, accuracy=3)

    def gen_orders(self, _type, _deep):
        match _type:
            case 'buy':
                rng = range(self.current_step - 1, self.current_step - _deep - 1, -1)
            case 'sell':
                rng = range(self.current_step + 1, self.current_step + _deep + 1)
            case _:
                print(RED, 'wrong gen_orders input type', END)
                return
        res = [{'rate': self.init_rate + (self.step * i),
                'amount_usd': bet * (mult ** (abs(i) - 1)),
                'amount': bet * (mult ** (abs(i) - 1)) / self.rate,
                'type': _type,
                'step': i,
                'diff': percent(self.init_rate, self.init_rate + (self.step * i), 3)} for i in rng]

        print(f'{WHITE}orders_{_type} {res} current_step={self.current_step}{END}')
        return res


if __name__ == '__main__':

    END = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    params = {
        'time_frames': {'30m': 1800},
        'frame': '30m',
        'pair': 'USDT_BTC',
        'from': '2021-02-01 00:00:00',
        'to': '2021-02-01 01:00:00',
    }

    step_percent = 0.05   # %
    mult = 3        # множитель следующей ставки
    deep = 5        # количество ставок в гриде в одну сторону
    bet = 10        # начальная ставка в 10 $ * rate
    fee = 0.01      # %

    data = Data(params)
    s = Session(data.tradebook[0]['rate'], deep, data.tradebook[0]['rate'] / 100 * step_percent)

    for trade in data.tradebook:
        print('-' * 80)
        s.rate = rate = trade['rate']
        amount = trade['amount']
        typ = trade['type']

        print(f'{trade} изменение на {GREEN if s.rate_diff >= 0 else RED}{s.rate_diff}%{END}, {s.prev_rate}')

        if rate > s.orders_sell[0]['rate']:
            """ цена пошла вверх, скупаем в шорт"""
            print(f'цена пошла ↑ на {s.rate_diff}% ({s.rate_full_diff}%)')

            if s.position:
                if s.position[0]['type'] == 'long':
                    """ закрываем long позицию """
                    print(f'{GREEN}закрываем long позицию {s.position}{END}')
                    # ЗДЕСЬ ФУНКЦИОНАЛ ЗАКРЫТИЯ ПОЗИЦИИ !

            if rate < s.orders_buy[-1]['rate']:
                print(f'{RED}Цена превысила пределы сетки orders_sell - закрываем ордера!{END}')
            else:
                for n, order in enumerate(s.orders_buy, 1):
                    if rate > order['rate']:
                        print(f'цена {rate} выше {n} уровня {order["rate"]}')
                        if s.max_reached_level < abs(n):
                            s.max_reached_level = abs(n)
                        if typ == 'buy':
                            if amount >= order['amount']:
                                print(f'ордер {n} удовлетворен rate: {order["rate"]} amount: {order["amount"]}')
                                s.position.append({'rate': order['rate'], 'amount': order['amount'], 'type': 'short'})
                                print(f'{CYAN}position {s.position}{END}')
                                s.orders_buy = [{'rate': s.rate_opposite, 'amount_usd': s.amount_opposite * order['rate'], 'amount': s.amount_opposite, 'type': 'buy', 'step': None, 'diff': None}]
                                print(f'{WHITE}orders_buy {s.orders_buy}{END}')
                                s.current_step = order['step']
                                s.orders_sell = s.gen_orders('sell', deep)
                                # print(f'Profit: {add_percent(order["amount"] * (s.orders_sell[0]["rate"] - s.position[0]["rate"]), -fee)}')
                            else:
                                print(f'ордер {n} не удовлетворен, малый amount {amount}')
                        else:
                            print('ордер не удовлетворен, произошла рыночная покупка')
                            break
                    else:
                        break
            input()

        if rate < s.orders_buy[0]['rate']:
            """ цена пошла вниз, скупаем в лонг"""
            print(f'цена ↓ на {s.rate_diff}% ({s.rate_full_diff}%)')

            if s.position:
                if s.position[0]['type'] == 'short':
                    """ закрываем short позицию """
                    print(f'{GREEN}закрываем short позицию {s.position}{END}')
                    # ЗДЕСЬ ФУНКЦИОНАЛ ЗАКРЫТИЯ ПОЗИЦИИ !

            if rate < s.orders_buy[-1]['rate']:
                print(f'{RED}Цена опустилась за пределы сетки orders_buy - закрываем ордера!{END}')
            else:
                for n, order in enumerate(s.orders_buy, 1):
                    if rate < order['rate']:
                        print(f'цена {rate} ниже {n} уровня {order["rate"]}')
                        if s.max_reached_level < abs(n):
                            s.max_reached_level = abs(n)
                        if typ == 'sell':
                            if amount >= order['amount']:
                                print(f'ордер {n} удовлетворен rate: {order["rate"]} amount: {order["amount"]}')
                                s.position.append({'rate': order['rate'], 'amount': order['amount'], 'type': 'long'})
                                print(f'{CYAN}position {s.position}{END}')
                                s.orders_sell = [{'rate': s.rate_opposite, 'amount_usd': s.amount_opposite * order['rate'], 'amount': s.amount_opposite, 'type': 'sell', 'step': None, 'diff': None}]
                                print(f'{WHITE}orders_sell {s.orders_sell}{END}')
                                s.current_step = order['step']
                                s.orders_buy = s.gen_orders('buy', deep)
                                # print(f'Profit: {add_percent(order["amount"] * (s.orders_sell[0]["rate"] - s.position[0]["rate"]), -fee)}')
                            else:
                                print(f'ордер {n} не удовлетворен, малый amount {amount}')
                        else:
                            print('ордер не удовлетворен, произошла рыночная покупка')
                            break
                    else:
                        break
            input()

        s.prev_rate = rate
