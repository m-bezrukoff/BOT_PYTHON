from multiprocessing.dummy import Pool as ThreadPool 
from itertools import repeat
from tqdm import tqdm
from math import ceil
from time import time, sleep
from ai.dataset_generator import load_charts_from_file
from simulator.playground import do_batch_job


def prepare_global_tasks():
    tasks = []
    for macd_in_fast in range(3, 14):
        for macd_in_slow in range(12, 30):
            for macd_in_signal in range(2, 9):
                for macd_out_fast in range(3, 14):
                    for macd_out_slow in range(12, 30):
                        for macd_out_signal in range(2, 9):
                            params = {
                                'macd_in_fast': macd_in_fast,
                                'macd_in_slow': macd_in_slow,
                                'macd_in_signal': macd_in_signal,

                                'macd_out_fast': macd_out_fast,
                                'macd_out_slow': macd_out_slow,
                                'macd_out_signal': macd_out_signal,

                                'ema_fast': 100,
                                'ema_slow': 200
                            }
                            tasks.append(params)
                            # tasks.append([macd_in_fast,
                            #               macd_in_slow,
                            #               macd_in_signal,
                            #               macd_out_fast,
                            #               macd_out_slow,
                            #               macd_out_signal,
                            #               100,
                            #               200])
    print('total tasks:', len(tasks))
    return tasks


def fn(charts, task, bar):
    print('\r\n', task)
    res = do_batch_job(charts, task, no_print=True)
    # res = {'profit': 2 * 2, 'params': task}
    bar.update()

    # if res['profit'] > -3:
    #     bar.add()
        # q.put({'profit': res['profit'], 'params': params})


if __name__ == '__main__':

    pair = 'BTC_ETH'
    charts = load_charts_from_file(pair=pair)

    start = 420000
    length = 8640
    charts = charts[start:start + length]
    tasks = prepare_global_tasks()

    bar = tqdm(total=len(tasks))
    pool = ThreadPool(6)
    results = list(pool.starmap(fn, zip(repeat(charts), tasks, repeat(bar))))
    pool.cache_c()
    pool.join()
