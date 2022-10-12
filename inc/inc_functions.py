from config import *
# from numba import njit
from datetime import datetime


# @njit
def percent(a, b, accuracy=8):
    # вычисляет разницу в % между a, b
    if not a:
        return 0
    x = -1 if (a < 0 or b < 0) else 1
    if a < b:
        res = abs(b-a) / a * 100 * x
    else:
        res = (a-b) / a * -100 * x
    return round(res, accuracy)


def add_percent(a, b):
    # добавляет к числу а, b процентов
    return round(a + (a / 100 * b), 8)


def percent_of_sum(a, b, num):
    # вычисляет долю 'a' в % суммы  a + b
    return round(a / (a + b) * 100, num)


def weighted_average(list_rate, list_amount):
    # взвешенное среднее значение (среднее с учетом объема)
    return sum(list_rate[i] * list_amount[i] / sum(list_amount) for i in range(len(list_rate)))


def average(lst):
    return sum(lst) / len(lst)


def decorator(fn):
    def wrapper(self):
        reserve = self.coins.balance_available(conf_base_coin)
        if reserve >= conf_trade_bounds['USDT']['amount_limit']:
            return fn(self)
        else:
            self.log.log(self.pair, 'Not enough money {}'.format(reserve))
    return wrapper


def get_buy_sell_type(typ):
    if typ in conf_sell_idx:
        return 'sell'
    if typ in conf_buy_idx:
        return 'buy'
    return False


def split(lst, n):
    k, m = divmod(len(lst), n)
    return list((lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)))
