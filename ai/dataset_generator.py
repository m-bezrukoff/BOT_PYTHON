from inc.inc_functions import percent, add_percent, weighted_average
from inc.inc_system import to2, find_candle_start_time
from pickle import load, dump
import numpy as np
import talib
from datetime import datetime


log_file = 'keras.txt'


def load_charts_from_file(pair='BTC_ETH'):
    with open('../charts/' + pair + '.dat', 'rb') as _file:
        charts = load(_file)
        print('{} loaded {} charts from file'.format(pair, len(charts)))
        return charts


def load_public_trades_from_file(pair='BTC_ETH'):
    with open('../save/test_' + pair + '.dat', 'rb') as _file:
        public_trades = load(_file)['trades']
        print('{} loaded {} public_trades from file'.format(pair, len(public_trades)))
        return public_trades


def multiline_saver(lst, pair):
    file = open('dataset_' + pair + '.txt', 'w', encoding="utf-8")
    file.writelines(lst)
    file.close()


def get_mean_discrete(lst):
    try:
        return 1 if (lst[-1] / (sum(lst) / len(lst))) > 2 else 0
    except ZeroDivisionError:
        return 0


def dataset_one_string_generator(lst, i, macd):
    x = [
        percent(lst[i]['low'], lst[i - 1]['low']),
        percent(lst[i - 1]['low'], lst[i - 2]['low']),
        percent(lst[i - 2]['low'], lst[i - 3]['low']),
        percent(lst[i - 3]['low'], lst[i - 4]['low']),
        percent(lst[i - 4]['low'], lst[i - 5]['low']),
        percent(lst[i - 5]['low'], lst[i - 6]['low']),

        # 1 if lst[i - 1]['close'] <= lst[i - 1]['open'] else 0,
        # 1 if lst[i - 2]['close'] <= lst[i - 2]['open'] else 0,
        # 1 if lst[i - 3]['close'] <= lst[i - 3]['open'] else 0,
        # 1 if lst[i - 4]['close'] <= lst[i - 4]['open'] else 0,
        # 1 if lst[i - 5]['close'] <= lst[i - 5]['open'] else 0,

        # percent(lst[i]['low'], lst[i]['high']),
        # percent(lst[i - 1]['low'], lst[i - 1]['high']),
        # percent(lst[i - 2]['low'], lst[i - 2]['high']),
        # percent(lst[i - 3]['low'], lst[i - 3]['high']),
        # percent(lst[i - 4]['low'], lst[i - 4]['high']),
        # percent(lst[i - 5]['low'], lst[i - 5]['high']),

        round(macd[i] * 10000, 2),
        round(macd[i-1] * 10000, 2),

        # percent(lst[i - 1]['close'], lst[i - 1]['open']),
        # percent(lst[i - 2]['close'], lst[i - 2]['open']),
        # percent(lst[i - 3]['close'], lst[i - 3]['open']),
        # percent(lst[i - 4]['close'], lst[i - 4]['open']),
        # percent(lst[i - 5]['close'], lst[i - 5]['open']),

        # get_mean_discrete([x['volume'] for x in lst[i - 10:i]])
        ]
    return x if not np.isnan(np.min(x)) else False


def dataset_generator(pair, lst, equalizer):
    # equalizer = 0  # соотношение положительных и отрицательных точек 1 => 1:1
    dataset = ''
    count_pos = 0
    count_neg = 0

    charts, arr_open, arr_close, arr_high, arr_low, arr_volume, xdate, ema, signal, macd, macd_colors = render_indicators(lst, 0, -1)

    len_lst = len(lst)
    percent = 0

    for i in range(len_lst):
        percent_new = round(i / len_lst * 100)
        if percent != percent_new:
            print('{} %'.format(percent_new))
            percent = percent_new
        try:
            res = dataset_one_string_generator(lst, i, macd)
            if res:
                if find_minimums(lst, i, arr_close, macd):
                    count_pos += 1
                    dataset += ' '.join(str(x) for x in res) + ' 1\n'
                else:
                    try:
                        if count_pos / count_neg > equalizer:
                            count_neg += 1
                            dataset += ' '.join(str(x) for x in res) + ' 0\n'
                    except ZeroDivisionError:
                        count_neg += 1
                        dataset += ' '.join(str(x) for x in res) + ' 0\n'
        except IndexError:
            pass

    multiline_saver(dataset, pair)
    print('total:', len_lst, 'positive:', count_pos, 'negative:', count_neg)

    return count_pos + count_neg - 10


def public_trades_buys(arr):
    points = {'x': [], 'y': [], 'unix_time': []}
    try:
        for i in arr:
            if i['type'] == 1:
                points['x'].append(i['date'])
                # points['x'].append(datetime.fromtimestamp(find_candle_start_time(i['date'])).strftime('%d %b %H:%M:%S'))
                points['y'].append(i['rate'])
    except KeyError:
        pass
    print('buy points:', len(points['x']))
    return points


def public_trades_sells(arr):
    points = {'x': [], 'y': [], 'unix_time': []}
    try:
        for i in arr:
            if i['type'] == 0:
                points['x'].append(i['date'])
                # points['x'].append(datetime.fromtimestamp(find_candle_start_time(i['date'])).strftime('%d %b %H:%M:%S'))
                points['y'].append(i['rate'])
    except KeyError:
        pass
    print('sell points:', len(points['x']))
    return points


if __name__ == "__main__":
    dataset_generator('BTC_ETH', 1, -1)
