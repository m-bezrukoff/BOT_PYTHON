from multiprocessing import Process, Queue, cpu_count

# from math import ceil
from time import sleep
from simulator.playground import do_batch_job, get_charts
from simulator.cls_progress_bar import ProgressBar
from simulator_v2.playground_indicators import render_indicators
import json


# def parting(xs, parts):
#     part_len = ceil(len(xs)/parts)
#     return [xs[part_len*k:part_len*(k+1)] for k in range(parts)]


def fn(c, i, t, r, f):
    while True:
        try:
            params = t.get(timeout=0.2)
            res = do_batch_job(c, i, params, no_print=True)
            if res['profit'] > 0:
                r.put({'profit': res['profit'], 'success': res['success'], 'profit_deals': res['profit_deals'], 'lose_deals': res['lose_deals'], 'params': params})
        except Exception as e:
            f.put(Process().name)
            break


def tasks_generator(t):
    # for ema_fast in range(10, 40):
    for macd_in_fast in [6]:
        for macd_in_slow in [21]:
            for macd_in_signal in [2]:
                for macd_out_fast in [4]:
                    for macd_out_slow in [26]:
                        for macd_out_signal in [2]:
                            for ema_fast in [10]:
                                for ema_slow in [16]:
                                    for stop_loss in [-0.9]:
                                        for in_lim_up in [round(0.996 + (i * 0.0001), 4) for i in range(int((1 - 0.996) / 0.0001))]:    # 0.8 - 1 c шагом 0.0002
                                            for in_lim_down in [round(0.2 + (i * 0.05), 4) for i in range(int((1.1 - 0.2) / 0.05))]:    # 0.2 - 1.1 c шагом 0.01
                                                # for out_lim_up in [-0.9]:
                                                #     for out_lim_down in [-0.9]:
                                                t.put({
                                                    'macd_in_f': macd_in_fast,
                                                    'macd_in_s': macd_in_slow,
                                                    'macd_in_sig': macd_in_signal,

                                                    'macd_out_f': macd_out_fast,
                                                    'macd_out_s': macd_out_slow,
                                                    'macd_out_sig': macd_out_signal,

                                                    'ema_f': ema_fast,
                                                    'ema_s': ema_slow,

                                                    'c_size': 300,
                                                    'stop_loss': stop_loss,
                                                    'in_lim_up': in_lim_up,
                                                    'in_lim_down': in_lim_down,
                                                    # 'out_lim_up': out_lim_up,
                                                    # 'out_lim_down': out_lim_down,
                                                })

    return t


def collecting_results(p, t, r, f, b):
    results = []

    while not f.qsize() == p:
        b.update(t.qsize())
        sleep(1)

    while not f.empty():
        print(f.get(), 'finished')

    while not r.empty():
        x = r.get()
        results.append(x)
    print('Finished all processes. Total results', len(results))
    return results


def show_best_results(r):
    profits = sorted([i['profit'] for i in r], reverse=True)
    print(profits[:50])
    res = [x for y in set(profits[:50]) for x in r if x['profit'] == y]
    res_sorted = sorted(res, key=lambda k: k['profit'], reverse=True)
    for _ in res_sorted:
        print(_)
    return res_sorted


def do_multiprocessing(p, c, i, t, r, f):
    print('\r\nprocessors {} of {}'.format(p, cpu_count()))
    print('total tasks:', t.qsize())
    processes = [Process(target=fn, args=(c, i, t, r, f)) for _ in range(p)]
    for _ in processes:
        _.start()
        print(_)


def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file)


if __name__ == '__main__':

    processors = 1
    tasks_queue = Queue()       # очередь заданий
    results_queue = Queue()     # очередь результаттов
    finish_queue = Queue()      # очередь флагов завершения процесса

    charts = get_charts('BTC_ETH', start=0, length=430000)
    # charts = get_charts('BTC_ETH', start=420000, length=8640)

    pp = {
        'macd_in_f': 6,
        'macd_in_s': 21,
        'macd_in_sig': 2,

        'macd_out_f': 4,
        'macd_out_s': 26,
        'macd_out_sig': 2,

        'ema_f': 10,
        'ema_s': 16,
    }
    indicators = render_indicators(charts, pp)

    tasks_queue = tasks_generator(tasks_queue)
    tasks_total = tasks_queue.qsize()
    bar = ProgressBar(tasks_total, model='reversed')

    do_multiprocessing(processors, charts, indicators, tasks_queue, results_queue, finish_queue)
    res = collecting_results(processors, tasks_queue, results_queue, finish_queue, bar)
    # save_json(str(res), 'simulation_unfiltered.dat')
    res_filtered = show_best_results(res)
    # print(''.join(res_filtered))
    # save_json(str(res_filtered), 'simulation_unfiltered.dat')
