#!/usr/bin/python
# coding: utf8

# import scipy as sp
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from pickle import dump, load, HIGHEST_PROTOCOL
from datetime import datetime

def return_typed_list(res):
    return [{'date': int(_['date']),
             'high': float(_['high']),
             'low': float(_['low']),
             'open': float(_['open']),
             'close': float(_['close']),
             'volume': float(_['volume']),
             'quoteVolume': float(_['quoteVolume']),
             'weightedAverage': float(_['weightedAverage'])} for _ in res]


# читаем данные
with open('../charts/BTC_ETH.dat', 'rb') as file:
    temp = return_typed_list(load(file))

# arr_close = [item['close'] for item in temp]
# self.arr_high = asarray([item['high'] for item in self.charts.data[300]])
# self.arr_low = asarray([item['low'] for item in self.charts.data[300]])
# self.arr_volume = asarray([item['volume'] for item in self.charts.data[300]])
# xdate = [datetime.fromtimestamp(item['date']).strftime('%d %b\n%H:%M:%S') for item in temp]

y = [int(i['close'] * 1000000) for i in temp]
# print(arr_close)
x = [i['date'] for i in temp]
# time_data = [i for i in range(len(data))]
# print(time_data)

# data = sp.genfromtxt("data.tsv", delimiter="\t")
# print(data[:10])  # часть данных можно напечатать, чтобы убедиться, что всё в порядке

# берём срезы: первую и вторую колонку нашего файла
# x = data[:, 0]
# y = data[:, 1]
#
# x = arr_close
# y = xdate

# настраиваем детали отрисовки графиков
plt.figure(figsize=(8, 6))
plt.title("price")
plt.xlabel("Days")
plt.ylabel("price")
#plt.xticks([...], [...]) # можно назначить свои тики
plt.autoscale(tight=True)

# рисуем исходные точки
plt.plot(x, y)

legend = []
# аргументы для построения графиков моделей: исходный интервал + 60 дней
fx = np.linspace(x[0], x[-1] + 100, 1000)


def polyn(deg=1):
    fp, residuals, rank, sv, rcond = np.polyfit(x, y, deg, full=True)
    f = np.poly1d(fp)
    plt.plot(fx, f(fx), linewidth=1)
    legend.append("d=%i" % f.order)


deg = 1

# while True:
#     polyn(deg)
#     deg = int(input('степень полинома: '))

for d in (1, 3, 15):
    polyn(d)

# for d in range(5, 12):
#     # получаем параметры модели для полинома степени d
#     fp, residuals, rank, sv, rcond = np.polyfit(x, y, 2, full=True)
#     f = np.poly1d(fp)
#     #print(f)
#     # рисуем график модельной функции
#     plt.plot(fx, f(fx), linewidth=1)
#     legend.append("d=%i" % f.order)
#     f2 = f - 1000   # из полинома можно вычитать
#     t = fsolve(f2, x[-1])   # ищем решение уравнения f2(x)=0, отплясывая от точки x[-1]
#     print("Полином %d-й степени:" % f.order)
#     print("- Мы достигнем 1000 установок через %d дней" % (t[0] - x[-1]))
#     print("- Через 60 дней у нас будет %d установок" % f(x[-1] + 60))

# plt.legend(legend, loc="upper left")
plt.grid()
# plt.savefig('data.png', dpi=50)
plt.show()
