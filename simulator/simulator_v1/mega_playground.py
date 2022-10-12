from multiprocessing import Process, Queue, current_process, cpu_count

from time import time, sleep
from simulator.playground import do_batch_job, get_charts, cut_by_time
from simulator.cls_progress_bar import ProgressBar
from inc.inc_system import save_pickle
from simulator_v2.playground_indicators import np, MACD
import talib as tb


# def parting(xs, parts):
#     part_len = ceil(len(xs)/parts)
#     return [xs[part_len*k:part_len*(k+1)] for k in range(parts)]

def multiline_saver(path, lst):
    if lst and path:
        s = ''
        for i in lst:
            s += str(i) + '\r'
        file = open(path, 'w', encoding="utf-8")
        file.writelines(s)
        file.close()


def frange(i, o, s):
    m = 10 ** max([abs(str(_).find('.') - len(str(_))) - 1 for _ in [i, o, s]])
    i = int(i * m)
    o = int(o * m)
    s = int(s * m)
    return [_ / m for _ in range(i, o, s)]


def fn(_ar, t, r, f):
    while True:
        try:
            params = t.get(timeout=0.2)
            # print(params)
            res = do_batch_job(_ar, params, mega=True)
            if res['success'] > 50 and res['profit'] > 0:
                _s = int(res['success'])
                _p = round(res['profit'], 1)
                _pd = res['profit_deals']
                _ld = res['lose_deals']
                _sc = int(_s * _p)
                r.put({'profit': _p, 'success': _s, 'score': _sc, 'profit_deals': _pd, 'lose_deals': _ld, 'params': params})
        except Exception as e:
            f.put(Process().name)
            break


def tasks_generator(t):
    # for ema_f in range(10, 200):
    #     for ema_s in range(16, 200):
    for in_lim_down in range(-70, -150, -5):
        for in_lim_up in range(-70, -140, -5):
            for out_lim_down in range(30, 90, 5):
                for out_lim_up in range(30, 90, 5):
                    # for stop_loss in frange(-1.2, -2.8, -0.2):
    # for macd_in_fast in range(2, 20):
    #     for macd_in_slow in range(2, 40):
    #         for macd_in_signal in range(2, 6):
    #             # for macd_out_fast in range(2, 12):
    #             #     for macd_out_slow in range(9, 30):
    #             #         for macd_out_signal in range(2, 6):
    #             for stop_loss in frange(-0.2, -2, -0.2):
    #
    #                     for out_lim_up in frange(0.3, 3, 0.1):
                    t.put({
                        # 'macd_in_f': macd_in_fast,
                        # 'macd_in_s': macd_in_slow,
                        # 'macd_in_sig': macd_in_signal,
                        #
                        # 'macd_out_f': macd_in_fast,
                        # 'macd_out_s': macd_in_slow,
                        # 'macd_out_sig': macd_in_signal,

                        # 'ema_f': ema_f,
                        # 'ema_s': ema_s,

                        'c_size': 300,
                        'stop_loss': -1.6,
                        # 'stop_loss': stop_loss,

                        'in_lim_down': in_lim_down,
                        'in_lim_up': in_lim_up,
                        'out_lim_down': out_lim_down,
                        'out_lim_up': out_lim_up,
                    })
    return t


def collecting_results(p, t, r, f, b):
    results = []

    while not f.qsize() == p:
        b.update(t.qsize())
        sleep(1)

    while not f.empty():
        print('\r', f.get(), 'finished')

    while not r.empty():
        x = r.get()
        results.append(x)
    print('Finished all processes. Total results', len(results))
    return results


def show_best_results(r):
    # best = sorted([i['score'] for i in r], reverse=True)
    # print(best)
    # res = [x for y in set(best[:50]) for x in r if x['points'] == y]
    res_sorted = sorted(res, key=lambda k: k['success'], reverse=True)
    for _ in res_sorted[:30]:
        print(_)
    max_profit = max([i['profit'] for i in res_sorted])
    max_success = max([i['success'] for i in res_sorted])
    max_score = max([i['score'] for i in res_sorted])
    print('max profit \033[32m{}\033[0m max success \033[32m{}\033[0m max score \033[32m{}\033[0m'
          .format(max_profit, max_success, max_score))
    return res_sorted[:10000]


def do_multiprocessing(p, _ar, t, r, f):
    print('\r\nprocessors {} of {}'.format(p, cpu_count()))
    print('total tasks:', t.qsize())
    processes = [Process(target=fn, args=(_ar, t, r, f)) for _ in range(p)]
    for _ in processes:
        _.start()
        print(_)


if __name__ == '__main__':
    processors = 11
    tasks_queue = Queue()       # очередь заданий
    results_queue = Queue()     # очередь результаттов
    finish_queue = Queue()      # очередь флагов завершения процесса

    # charts = get_charts('BTC_ETH', start=0, length=430000)
    # charts = get_charts('BTC_ETH', start=400000, length=8640 * 3)
    charts = get_charts('USDT_BTC', start=550000, length=8640)

    # charts = cut_by_time(get_charts('USDT_BTC'), 1525974900, 8640)

    ar = dict()
    ar['charts'] = charts
    ar['open'] = np.asarray([item['open'] for item in charts])
    ar['close'] = np.asarray([item['close'] for item in charts])
    ar['high'] = np.asarray([item['high'] for item in charts])
    ar['low'] = np.asarray([item['low'] for item in charts])
    ar['xdate'] = [graphics_time(item['date']) for item in charts]
    ar['unix_time'] = [int(item['date']) for item in charts]
    ar['bb_u_2'], ar['bb_m_2'], ar['bb_l_2'] = tb.BBANDS(ar['close'], timeperiod=16, nbdevup=2, nbdevdn=2, matype=0)
    ar['macd_in'], ar['macd_in_s'], ar['macd_in_h'], ar['macd_in_c'] = MACD(ar['close'], fast=8, slow=17, signal=9)
    ar['macd_out'], ar['macd_out_s'], ar['macd_out_h'], ar['macd_out_c'] = MACD(ar['close'], fast=8, slow=17, signal=9)
    ar['range'] = range(len(ar['charts']))
    # ar['ema_f'] = EMA(ar['close'], period=10)
    # ar['ema_s'] = EMA(ar['close'], period=16)

    tasks_queue = tasks_generator(tasks_queue)
    tasks_total = tasks_queue.qsize()
    bar = ProgressBar(tasks_total, model='reversed')

    do_multiprocessing(processors, ar, tasks_queue, results_queue, finish_queue)
    res = collecting_results(processors, tasks_queue, results_queue, finish_queue, bar)
    res_filtered = show_best_results(res)
    multiline_saver('test_ema.txt', res_filtered)
