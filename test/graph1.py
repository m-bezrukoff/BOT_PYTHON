import numpy
import talib
import requests
import json
import time

from mpl_finance import candlestick2_ohlc
import matplotlib.animation as animation

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import datetime

BEAR_PERC = 70
BULL_PERC = 30

PAIR = 'BTC_ETH'

fig, ax = plt.subplots(3, sharex=True)
fig.comment = plt.figtext(.7, .05, '')


def update_graph(interval):
    start_time = time.time() - 15 * 60 * 60
    resource = requests.get(
        "https://poloniex.com/public?command=returnChartData&currencyPair=%s&start=%s&end=9999999999&period=300" % (
        PAIR, start_time))
    data = json.loads(resource.text)

    quotes = {}
    quotes['open'] = numpy.asarray([item['open'] for item in data])
    quotes['close'] = numpy.asarray([item['close'] for item in data])
    quotes['high'] = numpy.asarray([item['high'] for item in data])
    quotes['low'] = numpy.asarray([item['low'] for item in data])

    xdate = [datetime.fromtimestamp(item['date']) for item in data]

    ax[0].xaxis.set_major_locator(ticker.MaxNLocator(6))

    def chart_date(x, pos):
        try:
            return xdate[int(x)]
        except IndexError:
            return ''

    ax[0].clear()
    ax[0].xaxis.set_major_formatter(ticker.FuncFormatter(chart_date))

    candlestick2_ohlc(ax[0], quotes['open'], quotes['high'], quotes['low'], quotes['close'], width=0.6)

    print(ax[0].get_xdata())
    fig.autofmt_xdate()
    fig.tight_layout()

    macd, macdsignal, macdhist = talib.MACD(quotes['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    ax[1].clear()
    ax[1].plot(macd, color="y")
    ax[1].plot(macdsignal)

    # idx = numpy.argwhere(numpy.diff(numpy.sign(macd - macdsignal)) != 0).reshape(-1) + 0
    idx = []
    inters = []

    for offset, elem in enumerate(macd):
        if offset in idx:
            inters.append(elem)
        else:
            inters.append(numpy.nan)
    ax[1].plot(inters, 'ro')

    ax[1].scatter(x=ax[0].get_xdata(), y=inters, c='b')

    hist_data = []
    max_v = 0

    for offset, elem in enumerate(macdhist):
        activity_time = False
        curr_v = macd[offset] - macdsignal[offset]
        if abs(curr_v) > abs(max_v):
            max_v = curr_v
        perc = curr_v / max_v

        if ((macd[offset] > macdsignal[offset] and perc * 100 > BULL_PERC)  # восходящий тренд
                or (
                        macd[offset] < macdsignal[offset] and perc * 100 < (100 - BEAR_PERC)
                )

        ):
            v = 1
            activity_time = True
        else:
            v = 0

        if offset in idx and not numpy.isnan(elem):
            # тренд изменился
            max_v = curr_v = 0  # обнуляем пик спреда между линиями
        hist_data.append(v * 1000)

    ax[2].clear()
    ax[2].fill_between([x for x in range(len(macdhist))], 0, hist_data, facecolor='green', interpolate=True)
    plt.gcf().texts.remove(fig.comment)
    fig.comment = plt.figtext(.7, .05, '%s %s%s' % (PAIR, time.ctime(), ' ТОРГУЕМ!!!! ' if activity_time else ''),
                              style='italic',
                              bbox={'facecolor': 'red' if activity_time else 'green', 'alpha': 0.5, 'pad': 10})


plt.show()
ani = animation.FuncAnimation(fig, update_graph, interval=1000)
