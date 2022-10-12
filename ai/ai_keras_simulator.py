from ai.dataset_generator import dataset_one_string_generator
from ai._keras import keras_model, keras_predict_class
from inc.inc_functions import add_percent
import numpy as np
from datetime import datetime
from re import findall


def render_test_data(dimension, charts, arr_open, arr_close, arr_high, arr_low, arr_volume, xdate, ema, signal, macd, macd_colors):

    filename = 'weights/temp.hdf5'
    # dimension = int(findall('(?<=dim_)\d+', filename)[0])
    my_model = keras_model(dimension, filename)
    print('dimension:', dimension)

    data = {'minimums': {'date': [], 'val': []}, 'predictions': {'date': [], 'val': []}}
    # print(charts[:5:])

    for i in range(10, len(charts)):
        try:
            if find_minimums(charts, i, arr_close, macd):
                data['minimums']['date'].append(xdate[i])
                data['minimums']['val'].append(float(charts[i]['low']))

            ai_in = (dataset_one_string_generator(charts, i, macd))
            if ai_in:
                ai_np_in = np.array(ai_in).reshape(1, dimension)
                ai_out = keras_predict_class(my_model, ai_np_in)
                print(i, 'ai_out', ai_out, type(ai_out))
                if ai_out:
                    data['predictions']['date'].append(xdate[i])
                    data['predictions']['val'].append(add_percent(float(charts[i]['low']), 0.15))

        except IndexError as err:
            print(err)

    return data

# def sim():
#     pair = 'BTC_ETH'
#     limit = 5600
#     _from = -1000
#     _to = -1
#     charts = load_charts_from_file(pair=pair, fr=_from, to=_to)
#     arr_open = np.asarray([item['open'] for item in charts])
#     arr_close = np.asarray([item['close'] for item in charts])
#     arr_high = np.asarray([item['high'] for item in charts])
#     arr_low = np.asarray([item['low'] for item in charts])
#     arr_volume = np.asarray([item['volume'] for item in charts])
#     xdate = [datetime.fromtimestamp(item['date']).strftime('%d %b\n%H:%M:%S') for item in charts]
#
#     ema, signal, hist, colors = MACD(arr_close, fast=12, slow=26, signal=7)
#
#     for i in range(len(charts)):
#         try:
#             if hist[]:
#                 data['minimums']['date'].append(int(charts[i]['timestamp']))
#                 data['minimums']['val'].append(float(charts[i]['low']))
#
#             ai_in = (dataset_one_string_generator(charts, i))
#             ai_np_in = np.array(ai_in).reshape(1, dimension)
#             ai_out = keras_predict(my_model, ai_np_in)[-1]
#             print(i, 'ai_out', ai_out)
#
#             if ai_out:
#                 data['predictions']['date'].append(int(charts[i]['timestamp']))
#                 data['predictions']['val'].append(add_percent(float(charts[i]['low']), 0.15))
#
#         except IndexError as err:
#             print(err)
#
#     return data, ema, signal, hist, colors
#
#     return charts, ema, signal, hist, colors, data


if __name__ == "__main__":
    # charts, ema, signal, hist, colors, data = sim()
    # do_plot(charts, points, ema, signal, hist, colors)
    pass
