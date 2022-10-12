from stocks.poloniex import poloniex_api
from inc.inc_system import time, sleep, utc_timestamp_to_date, utc_date_to_timestamp, save_zipped_pickle, load_zipped_pickle
import os
from multiprocessing import Process, Queue, cpu_count, Lock
from simulator_v1.cls_progress_bar import ProgressBar
from classes.cls_charts import get_charts_formatted


def gen_map(_from, _charts):
    t = time()
    print('----------------------------------------------')
    print('generating map')
    start = (int(_from) // candle_size) * candle_size
    end = (int(time()) // candle_size) * candle_size
    _need = {_ for _ in range(start, end, candle_size)}
    _have = {_['timestamp'] for _ in _charts}
    _left = sorted(list(_need.difference(_have)))
    print('total candles: {}, already loaded: {}, left to load: {}'.format(len(_need), len(_have), len(_left)))
    print('generating map took', round(time() - t1, 2), 'sec')
    # print(_left)
    return _left


def tasks_generator(_queue, _map):
    print('----------------------------------------------')
    print('generating {} tasks'.format(len(_map)))
    _lim = 0
    for i in _map:
        if i > _lim:
            _lim = i + (1000 * candle_size)
            _queue.put([i, _lim])

    print('total generated tasks:', _queue.qsize())
    print('tasks_generator took', round(time()-t1, 2), 'sec')
    return _queue


def do_multiprocessing(pr, p, c, _tasks, r, f):
    print('\r\nprocessors {} of {}'.format(pr, cpu_count()))
    print('total tasks:', _tasks.qsize())
    processes = [Process(target=downloader, args=(p, c, _tasks, r, f)) for _ in range(pr)]
    for _ in processes:
        _.start()
        print(_)


def downloader(p, c, t, r, f):
    pol = poloniex_api.PoloniexPublic()
    while True:
        try:
            params = t.get(timeout=1)
            res = pol.returnChartData(p, c, params[0], params[1])
            print('get {} - {}   {} - {} -> {} lines'.format(
                params[0],
                params[1],
                utc_timestamp_to_date(params[0]),
                utc_timestamp_to_date(params[1]),
                len(res) if res else 0))
            if res:
                formatted_res = get_charts_formatted(res)
                for i in formatted_res:
                    if i['timestamp'] != 0:
                        r.put(i)
            else:
                print('failed to load', params)
                f.put(Process().name)
        except Exception as e:
            f.put(Process().name)
            break


def collecting_results(p, t, r, f, b):
    results = []

    while not f.qsize() == p:
        b.update(t.qsize())
        sleep(1)

    while not f.empty():
        print('\r', f.get(), 'finished')

    print('----------------------------------------------')
    print('collecting results')
    t1 = time()

    while not r.empty():
        x = r.get()
        results.append(x)
    print('Finished all processes. Total results', len(results))
    print('collecting results took', round(time() - t1, 2), 'sec')
    return results


def process_results(c, r):
    print('----------------------------------------------')
    print('process_results - charts: {} results: {}'.format(len(c), len(r)))
    print('consolidating...')
    t1 = time()
    dates = set()

    _need = {_['timestamp'] for _ in r}
    _have = {_['timestamp'] for _ in c}
    _left = _need.difference(_have)

    print('candles to add:', len(_left))

    for i in r:
        if i['timestamp'] not in dates and i['timestamp'] != 0:
            c.append(i)
            dates.add(i['timestamp'])
    print('process_results - charts after consolidating: {}'.format(len(c)))
    print('consolidating took', round(time() - t1, 2), 'sec')

    print('----------------------------------------------')
    print('sorting...')
    c = sorted(c, key=lambda k: k['timestamp'])
    print('process_results - sorted', [c[i]['timestamp'] for i in range(5)])
    print('sorting took', round(time() - t1, 2), 'sec')
    return c


def fix_charts(_charts):
    print('----------------------------------------------')
    print('fix charts')
    t1 = time()
    c = []
    t = time()
    c.append(_charts[0])
    for i in range(1, len(_charts)):
        if _charts[i]['timestamp'] > _charts[i - 1]['timestamp']:
            c.append(_charts[i])
    print('charts is OK ({}/{}), time: {} sec'.format(len(_charts), len(c), round(time() - t, 2)))
    print('fix charts took', round(time() - t1, 2), 'sec')
    return c


def trim_charts(_charts, _from):
    print('----------------------------------------------')
    print('trim charts')
    t = time()
    c = 0
    while True:
        if _charts[0]['timestamp'] < _from:
            _charts.pop(0)
            c += 1
        else:
            break
    if c > 0:
        print('charts trimmed for {} candles'.format(c))
    else:
        print('charts is OK')
    return _charts


def check_consistency(c):
    print('----------------------------------------------')
    print('checking consistency')
    t1 = time()
    o = True
    for i in range(1, len(c)):
        if not c[i]['timestamp'] - candle_size == c[i - 1]['timestamp']:
            o = False
            print('\033[31m{} - {}  {} - {} error in {}  \033[0m'.format(c[i-1]['timestamp'], c[i]['timestamp'], c[i-1]['utc_date'], c[i]['utc_date'], i))
    if o:
        print('\033[32mconsistency is OK {} {}\033[0m'.format(c[0]['utc_date'], c[-1]['utc_date']))
    print('checking consistency took', round(time() - t1, 2), 'sec')
    return o


def save_candles(_file_path, _charts):
    print('----------------------------------------------')
    print('save candles')
    t1 = time()
    save_zipped_pickle(_file_path, _charts)
    print(file_path, 'file saved')
    print('save candles took', round(time() - t1, 2), 'sec')


def show_slice(c, f, t):
    for i in c:
        if f <= i['timestamp'] <= t:
            print(i)


if __name__ == '__main__':

    processors = 3
    tasks_queue = Queue()       # очередь заданий
    results_queue = Queue()     # очередь результаттов
    finish_queue = Queue()      # очередь флагов завершения процесса
    lock = Lock()

    conf_time_frames = {'5m': 300, '30m': 1800}
    # conf_time_frames = {'30m': 1800}
    pairs = {
        'USDT_TRX': '2019-11-14 00:00:00',
        'USDT_BTC': '2015-03-01 00:00:00',
        # 'USDT_ETH': '2016-03-01 00:00:00',
    }

    t1 = time()

    for pair in pairs:
        print(pair)
        file_path = '../simulator/save/' + pair + '_charts.dat'
        fr = utc_date_to_timestamp(pairs[pair])

        if os.path.isfile(file_path) and os.path.getsize(file_path) > 0:
            charts = load_zipped_pickle(file_path)
        else:
            charts = {i: [] for i in conf_time_frames}

        flag_save_file = False
        for frame in conf_time_frames:
            candle_size = conf_time_frames[frame]
            print('################################################################################')
            print('                        {}  timeframe:  {}'.format(pair, frame))
            print('################################################################################')
            if charts.get(frame):
                charts_frame = charts[frame]
            else:
                charts_frame = []
            res = []
            consist = True
            to = int(time())

            if charts_frame:
                print('now in frame {}: {} candles ({} - {})'.format(
                    frame, len(charts_frame), charts_frame[0]['utc_date'], charts_frame[-1]['utc_date']))
            else:
                charts_frame = []
                print('charts frame {} is empty'.format(frame))

            if charts_frame:
                charts_frame = trim_charts(charts_frame, fr)
            full_map = gen_map(fr, charts_frame)

            if full_map:
                tasks_queue = tasks_generator(tasks_queue, full_map)
                tasks_total = tasks_queue.qsize()
                bar = ProgressBar(tasks_total, model='reversed')

                if tasks_total:
                    if tasks_total // processors < 2:
                        prc = 1
                    else:
                        prc = processors
                    do_multiprocessing(prc, pair, candle_size, tasks_queue, results_queue, finish_queue)
                    res = collecting_results(prc, tasks_queue, results_queue, finish_queue, bar)
                charts_filtered = process_results(charts_frame, res)
                charts_filtered = fix_charts(charts_filtered)
                check_consistency(charts_filtered)
                charts[frame] = charts_filtered
                flag_save_file = True

        if flag_save_file:
            save_candles(file_path, charts)
