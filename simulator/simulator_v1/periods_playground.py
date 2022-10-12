# from ai._keras_train import keras_train_complex
# from ai.ai_keras_simulator import render_test_data
from ai.dataset_generator import load_charts_from_file
from statistics import mean
from simulator.playground import do_batch_job
from inc.inc_system import utc_timestamp_to_date


def get_charts(pair, start=None, length=None):
    if start and length:
        return load_charts_from_file(pair=pair)[start:start + length]
    else:
        return load_charts_from_file(pair=pair)


# def do_batch_job(_ar, params, mega=False):
#     _ar = render_mega_indicators(_ar, params) if mega else render_indicators(_ar['charts'], params)
#     points_in = find_enter_bbands(_ar, params, mega)
#     points_out = find_exit_bbands(_ar, params, mega)
#     # points_in = find_enter_points(_ar, params, mega)
#     # mins = find_minimums(indicators)
#     # points_out = find_exit_points(_ar, params, mega)
#     profit = profit_calculator(_ar['charts'], params, points_in, points_out, mega)
#     return {'profit': profit[0], 'success': profit[1], 'profit_deals': profit[2], 'lose_deals': profit[3], 'points_in': points_in, 'points_out': points_out, 'indicators': _ar, 'params': params}


if __name__ == '__main__':
    periods = 36
    period = 8640

    charts = get_charts('USDT_BTC')
    print('start:', charts[0]['utc_date'])

    params = {
        'macd_in_f': 8,
        'macd_in_s': 17,
        'macd_in_sig': 9,

        'macd_out_f': 8,
        'macd_out_s': 17,
        'macd_out_sig': 9,

        # 'ema_f': 180,
        # 'ema_s': 108,

        'c_size': 300,
        'stop_loss': -1.6,
        'in_lim_down': -135,
        'in_lim_up': -125,
        'out_lim_up': 65,
        'out_lim_down': 65,
    }

    ar = dict()
    res = []

    for i in range(periods):
        _fr = len(charts) - ((periods - i) * period)
        _to = _fr + period
        ar['charts'] = charts[_fr:_to]
        ar['range'] = range(len(ar['charts']))
        print(ar['charts'][0])
        # ar['open'] = np.asarray([item['open'] for item in charts])
        # ar['close'] = np.asarray([item['close'] for item in charts])
        # ar['high'] = np.asarray([item['high'] for item in charts])
        # ar['low'] = np.asarray([item['low'] for item in charts])
        # ar['xdate'] = [graphics_time(item['date']) for item in charts]
        # ar['unix_time'] = [int(item['date']) for item in charts]
        # ar['ema_f'] = EMA(ar['close'], period=10)
        # ar['ema_s'] = EMA(ar['close'], period=16)

        res.append(do_batch_job(ar, params))

    av_profit = []
    av_success = []
    av_profit_deals = []
    av_lose_deals = []
    print('\r\n----------------------------------------')
    for i in res:
        av_profit.append(i['profit'])
        av_success.append(i['success'])
        av_profit_deals.append(i['profit_deals'])
        av_lose_deals.append(i['lose_deals'])

        print('{} {} profit {}% success {} ({}/{})'.format(i['arr']['charts'][0]['timestamp'],
                                                          i['arr']['charts'][0]['utc_date'],
                                                          i['profit'],
                                                          i['success'],
                                                          i['profit_deals'],
                                                          i['lose_deals']))

    print('----------------------------------------')
    print('total profit {} success {} ({}/{})'.format(round(sum(av_profit), 2),
                                                      round(mean(av_success), 2),
                                                      round(mean(av_profit_deals), 2),
                                                      round(mean(av_lose_deals), 2)))
