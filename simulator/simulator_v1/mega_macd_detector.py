from multiprocessing import Process, Queue, cpu_count

from time import sleep
from simulator.cls_progress_bar import ProgressBar
from simulator.playground import get_charts
from simulator_v2.playground_indicators import np, MACD


def multiline_saver(path, lst):
    if lst and path:
        s = ''
        for i in lst:
            s += str(i) + '\r'
        # s = '\r\n'.join(lst)
        file = open(path, 'a', encoding="utf-8")
        # lst = map(lambda x: x + '\n', lst)
        file.writelines(s)
        file.close()


def append_point(lst, t):
    lst['unix_time'].append(t)
    return lst


def find_minimums(arr):
    points = set()
    try:
        for i in range(len(arr['l'])):
            if arr['l'][i] < min([arr['l'][i-_] for _ in range(1, 90)]):
                if arr['l'][i] < min([arr['l'][i+_] for _ in range(1, 90)]):
                    points.add(arr['t'][i])
                    points.add(arr['t'][i+1])
                    points.add(arr['t'][i+2])

    except IndexError as err:
        pass
    return points


def find_enter_points(_ar):
    points = set()
    try:
        for i in range(len(_ar['l'])):
            if _ar['macd_in_h'][i - 1] < 0 < _ar['macd_in_h'][i] and _ar['macd_in'][i] < 0:
                points.add(_ar['t'][i])
    except KeyError as err:
        pass
    return points


def render_macd_indicators(_ar, par):
    macd_in, macd_in_s, macd_in_h, macd_in_c = MACD(_ar['c'], fast=par['macd_in_f'], slow=par['macd_in_s'], signal=par['macd_in_sig'])

    _ar['macd_in'] = macd_in
    _ar['macd_in_s'] = macd_in_s
    _ar['macd_in_h'] = macd_in_h
    _ar['macd_in_c'] = macd_in_c
    _ar['par'] = par
    return _ar


def macd_batch_job(_ar, params):
    indicators = render_macd_indicators(_ar, params)
    points_in = find_enter_points(indicators)
    hits = match_detector(_ar['actual'], points_in)

    hits = len(hits)
    total = len(points_in)
    try:
        ratio = round(hits / total, 4)
    except ZeroDivisionError:
        ratio = 0

    return {'hits': hits, 'total': total, 'ratio': ratio, 'params': params}


def match_detector(a, p):
    return a.intersection(p)


def fn(_ar, t, r, f):
    while True:
        try:
            params = t.get(timeout=0.2)
            res = macd_batch_job(_ar, params)
            if res['hits'] > 15:
                r.put(res)
        except Exception as e:
            print(e)
            f.put(Process().name)
            break


def tasks_generator(t):
    for macd_in_fast in range(2, 50):
        for macd_in_slow in range(3, 50):
            for macd_in_signal in range(2, 10):
                t.put({
                    'macd_in_f': macd_in_fast,
                    'macd_in_s': macd_in_slow,
                    'macd_in_sig': macd_in_signal,
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


def do_multiprocessing(p, _ar, t, r, f):
    print('\r\nprocessors {} of {}'.format(p, cpu_count()))
    print('total tasks:', t.qsize())

    processes = [Process(target=fn, args=(_ar, t, r, f)) for _ in range(p)]
    for _ in processes:
        _.start()
        print(_)


def show_best_results(r):
    # results = sorted([i['ratio'] for i in r], reverse=True)
    # print(results)
    # res = [x for y in set(results[:50]) for x in r if x['profit'] == y]
    res = list(r)
    res_sorted = sorted(res, key=lambda k: k['hits'])
    for _ in res_sorted[500:]:
        print(_)
    return res_sorted


if __name__ == '__main__':
    processors = 11
    tasks_queue = Queue()       # очередь заданий
    results_queue = Queue()     # очередь результаттов
    finish_queue = Queue()      # очередь флагов завершения процесса

    charts = get_charts('USDT_BTC', start=550000, length=8640)

    ar = dict()
    ar['charts'] = charts
    ar['o'] = np.asarray([item['open'] for item in charts])
    ar['c'] = np.asarray([item['close'] for item in charts])
    ar['h'] = np.asarray([item['high'] for item in charts])
    ar['l'] = np.asarray([item['low'] for item in charts])
    ar['t'] = [int(item['date']) for item in charts]
    ar['actual'] = actual = {1590159600, 1590237300, 1590279000, 1590365100, 1590404700, 1590509100, 1590616800, 1590653400, 1590750300, 1590809400, 1590871200, 1590968700, 1591014300, 1591111800, 1591162200, 1591193700, 1591270500, 1591358100, 1591404000, 1591462500, 1591539000, 1591604400, 1591662300, 1591699800, 1591781700, 1591815300, 1591895100, 1591984200, 1592022600, 1592078700, 1592145900, 1592202900, 1592319900, 1592363400, 1592424600, 1592538600, 1592598000, 1592652000}

    tasks_queue = tasks_generator(tasks_queue)
    tasks_total = tasks_queue.qsize()
    bar = ProgressBar(tasks_total, model='reversed')

    do_multiprocessing(processors, ar, tasks_queue, results_queue, finish_queue)
    res = collecting_results(processors, tasks_queue, results_queue, finish_queue, bar)
    res_filtered = show_best_results(res)
    multiline_saver('macd_test1.txt', res_filtered)
