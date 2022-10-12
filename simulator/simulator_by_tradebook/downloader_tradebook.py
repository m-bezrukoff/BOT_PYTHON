import os
from inc.inc_system import sleep, utc_date_to_timestamp, time, load_zipped_pickle, utc_timestamp_to_date, to2, save_zipped_pickle
from stocks.poloniex import poloniex_api
from multiprocessing import Process, Queue, Lock, current_process
from pprint import pprint


def get_formatted_trades(date, trade_id, typ, rate, amount):
    return {'date': int(date), 'id': int(trade_id), 'type': typ, 'rate': float(rate), 'amount': float(amount)}


def remove_dubs_and_sort(_tradebook):
    t1 = time()
    dat = list({i['id']: i for i in _tradebook}.values())  # удаляем дубликаты
    dat.sort(key=lambda k: k['id'])
    print('cleaned and sorted in {} sec'.format(to2(time() - t1)))
    return dat


def consistency(_tradebook):
    missed = {}
    for i in range(-1, -len(_tradebook), -1):
        if _tradebook[i]['id'] - _tradebook[i-1]['id'] != 1:
            missed[_tradebook[i]['date']] = {
                'date': [utc_timestamp_to_date(_tradebook[i-1]['date']), utc_timestamp_to_date(_tradebook[i]['date'])],
                'id': [_tradebook[i-1]['id'], _tradebook[i]['id']],
                'time': [_tradebook[i-1]['date'], _tradebook[i]['date']]
            }
    if missed:
        print('\033[31mwrong consistency:')
        pprint(missed)
        print('\033[0m')
    else:
        print('{}consistency is OK{}'.format(c['green'], c['end']))
    return missed


def partition(lst, threads, lim=60*20):
    fr = max(lst)
    to = min(lst)
    division = (fr - to) / threads
    if division > lim:
        return [[round(to + division * i), round(to + division * (i + 1))] for i in range(threads)]
    return [[to, fr]]


def gen_map():
    print('----------------------------------------------')
    print('generating map')
    t1 = time()
    print('range to process: {} - {}'.format(utc_timestamp_to_date(start_time), utc_timestamp_to_date(int(time()))))
    res = []

    if tradebook:
        # диапазон после скачанного трейдбука
        range_after = [tradebook[-1]['date'], int(time())]  # от конца трейдбука до текущего времени
        res.extend(partition(range_after, processes))

        # диапазон перед скачанным трейдбуком
        if tradebook[0]['date'] > start_time:
            range_before = [start_time, tradebook[0]['date']]  # от начала периода до начала трейдбука
            res.extend(partition(range_before, processes))
    else:
        res = [[start_time, int(time())]]

    if missed:
        for i in missed.keys():
            res.extend(partition(missed[i]['time'], processes))

    if res:
        print('map:')
        for i in range(len(res)):
            print(utc_timestamp_to_date(res[i][0]), '-', utc_timestamp_to_date(res[i][-1]))
        print('map generated in {} sec'.format(to2(time() - t1)))
    return res


def do_multiprocessing():
    print('----------------------------------------------')
    print('multiprocessing')
    print('total tasks:', tasks_queue.qsize())
    print_lock = Lock()
    for _ in range(processes):
        proc = Process(target=downloader, args=(pair, tasks_queue, results_queue, finish_queue, print_lock))
        proc.name = 'downloader #{}'.format(_)
        processes_list.append(proc)
        proc.start()
        print(proc)


def downloader(pair, tasks_queue, results_queue, finish_queue, lock):
    pol = poloniex_api.PoloniexPublic()
    err = 0
    while not tasks_queue.empty():
        try:
            rng = tasks_queue.get(timeout=2)
            to = min(rng)
            fr = max(rng)
            while True:
                if err > 2:
                    break
                lock.acquire()
                print('returnTradeHistory:', to, fr)
                lock.release()
                # res = []
                res = pol.returnTradeHistory(pair, fr - 30 * 24 * 3600, fr)
                lock.acquire()
                print('res count:', len(res), res[0])
                lock.release()
                if res:
                    out = [get_formatted_trades(int(utc_date_to_timestamp(i['date'])), i['tradeID'], i['type'], i['rate'], i['amount']) for i in res]
                    results_queue.put(out)
                    fr = int(utc_date_to_timestamp(res[-1]['date'])) + 1
                    err = 0
                    if to > fr:
                        break
                else:
                    err += 1
                    lock.acquire()
                    print('\033[31mres is empty at: {} - {}\033[0m'.format(fr, to))
                    lock.release()
                    sleep(0.5)

        except poloniex_api.PoloniexException as e:
            if 'maintenance mode' in str(e):
                print('{}{}{}'.format('\033[32m', e, '\033[0m'))
                break

        except Exception as e:
            if not e:
                print('\033[31mrequest error {}\033[0m'.format(e))
            break

    finish_queue.put(current_process().name)
    print('{}process {} finished!{}'.format('\033[32m', current_process().name, '\033[0m'))


def collecting_results():
    print('----------------------------------------------')
    print('collecting results')
    res = []
    while not finish_queue.qsize() == processes:
        # bar.update(tasks_queue.qsize())
        try:
            res.extend(results_queue.get())
        except Exception:
            pass

    while not finish_queue.empty():
        print(finish_queue.get(), 'finished')

    t1 = time()
    print('Total results_queue', results_queue.qsize())

    while not results_queue.empty():
        res.extend(results_queue.get())

    print('{}Finished all processes. Total results {}{}'.format(c['green'], len(res), c['end']))
    print('collecting results took', round(time() - t1, 2), 'sec')
    return res


def load_tradebook(_path):
    if os.path.isfile(_path) and os.path.getsize(_path) > 0:
        return load_zipped_pickle(_path)
    else:
        return []


def save_tradebook(_path, _dat):
    print('saving file', _path)
    t1 = time()
    save_zipped_pickle(_path, _dat)
    print('saved successfully in {} sec'.format(to2(time() - t1)))


def tasks_generator():
    print('----------------------------------------------')
    print('generating {} tasks'.format(len(full_map)))
    t1 = time()
    for i in full_map:
        tasks_queue.put(i)
    print('total generated tasks:', tasks_queue.qsize())
    return tasks_queue.qsize()


def consolidate_results(_new, _tradebook):
    print('----------------------------------------------')
    print('consolidating...')
    print('already have: {} gathered now: {}'.format(len(_tradebook), len(_new)))
    t1 = time()
    _tradebook.extend(_new)
    _consolidated = remove_dubs_and_sort(_tradebook)
    print('tradebook after consolidating: {}'.format(len(_consolidated)))
    print('consolidating took', round(time() - t1, 2), 'sec')
    return _consolidated


if __name__ == '__main__':
    # на Poloniex в запросе https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_ETH&start=1612580400&end=1612569900
    # не важна, очередность ОТ и ДО. Результат всегда возвращается 1000 записей от наиболее свежей даты.

    pairs = {
        # 'USDT_BTC': '2015-03-01 00:00:00',
        'USDT_BTC': '2018-12-01 00:00:00',
        # 'USDT_TRX': '2019-11-14 00:00:00',
        # 'USDT_ETH': '2016-03-01 00:00:00',
    }

    c = {
        'red': '\033[31m',
        'green': '\033[32m',
        'end': '\033[0m'
    }

    processes = 3

    for pair in pairs:
        file_path = '../simulator/save/' + pair + '_tradebook.dat'
        start_time = utc_date_to_timestamp(pairs[pair])
        tradebook = load_tradebook(file_path)
        missed = consistency(tradebook)
        processes_list = []

        tasks_queue = Queue()    # очередь заданий
        results_queue = Queue()  # очередь результаттов
        finish_queue = Queue()   # очередь флагов завершения процесса

        if tradebook:
            print('downloaded tradebook: {} - {}'.format(utc_timestamp_to_date(tradebook[0]['date']), utc_timestamp_to_date(tradebook[-1]['date'])))

        full_map = gen_map()
        tasks_total = tasks_generator()
        # bar = ProgressBar(tasks_total, model='reversed')
        if tasks_total:
            do_multiprocessing()
            new_results = collecting_results()
            consolidated = consolidate_results(new_results, tradebook)
            check = consistency(consolidated)
            save_tradebook(file_path, consolidated)
    print('done')
