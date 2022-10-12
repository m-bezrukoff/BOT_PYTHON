import sys
from playground_data import Data
from playground import Worker
from multiprocessing import Queue, Process
from tqdm import tqdm
from xls_export import Exporter
import keyboard
from inc.inc_system import *
import copy


def load_hash_list():
    _file_name = 'reports/hash.txt'
    try:
        _file = open(_file_name, 'r+')
        _set = set(_file.read().split('\n'))
        print('hash list size:', len(_set))
        _file.close()
        return _set
    except Exception:
        _file = open(_file_name, 'a+')
        _file.close()
        return set()


def do_multiprocessing(_data):
    print('\r\nCalculating in {} threads ...'.format(processors))
    _processes = []
    for i in range(processors):
        process = Process(target=worker, args=(tasks_queue, results_queue, _data))
        process.start()
        _processes.append(process)
    return _processes


def worker(_tasks_queue, _results_queue, _data):
    while not _tasks_queue.empty():
        _params = _tasks_queue.get()
        w = Worker(_params, copy.deepcopy(_data), printer=False)
        _results_queue.put(w.summary.result)


def terminate():
    for process in processes:
        process.kill()
    sys.exit(0)


def save_hash(dat):
    file = open('reports/hash.txt', 'a')
    for i in dat:
        file.write(str(i) + '\n')
    file.close()


def make_hash(par):
    h = hashlib.md5(str(par).encode())
    return h.hexdigest()


def collecting_results(size):
    hash_cache = set()
    results_to_collect = size
    results_collected = 0
    while results_collected != size:
        sleep(0.01)

        if results_to_collect > tasks_queue.qsize():
            bar.update(results_to_collect - tasks_queue.qsize())
            results_to_collect = tasks_queue.qsize()

        if results_queue.qsize():
            result = results_queue.get()
            results_collected += 1
            hash_cache.add(result['hash'])
            if result['ratio'] > 50:
                export.update_xlx_results(result)
                # print(result)

        if len(hash_cache) > 500:
            save_hash(hash_cache)
            hash_cache.clear()

        if keyboard.is_pressed('ctrl+q'):
            print('\r\nuser interrupted, saving results ...')
            # for process in processes:
            #     process.terminate()
            while not tasks_queue.empty():
                tasks_queue.get()

            while not results_queue.empty():
                result = results_queue.get()
                hash_cache.add(result['hash'])
                export.update_xlx_results(result)

            save_hash(hash_cache)
            export.save_xls_file()
            print('\r\n', '-' * 40, '\r\n')
            break

    save_hash(hash_cache)
    export.save_xls_file()
    bar.close()
    print('Finished all processes')


def task_generator(parameters):
    for ema_f in range(4, 25):
        for ema_m in range(8, 30):
            for ema_f_phase in [-100, -50, 0, 50, 100]:
                for ema_f_power in [1, 2, 3, 4]:
                    for ema_m_phase in [-100, -50, 0, 50, 100]:
                        for ema_m_power in [1, 2, 3, 4]:
                            if ema_f <= ema_m:
                                parameters['ema_f'] = ema_f
                                parameters['ema_f_phase'] = ema_f_phase
                                parameters['ema_f_power'] = ema_f_power
                                parameters['ema_m'] = ema_m
                                parameters['ema_m_phase'] = ema_m_phase
                                parameters['ema_m_power'] = ema_m_power

                                _hash = make_hash(parameters)
                                parameters['hash'] = _hash          # не учитывается в расчете hash

                                if _hash not in done_tasks_hash_set:
                                    tasks_queue.put(parameters.copy())   # обязательно снимать копию! иначе кладёт один и тот же таск

    # # единичный таск для тестирования
    # parameters['hash'] = '2325235235235235235235235235'
    # parameters['ema_f'] = 6
    # parameters['ema_f_phase'] = 50
    # parameters['ema_f_power'] = 1
    # parameters['ema_m'] = 15
    # parameters['ema_m_phase'] = 100
    # parameters['ema_m_power'] = 3
    # parameters['sleep'] = 0
    # tasks_queue.put(parameters.copy())
    #
    # # единичный таск для тестирования
    # parameters['hash'] = '2325232342344233252789723891'
    # parameters['ema_f'] = 5
    # parameters['ema_f_phase'] = 50
    # parameters['ema_f_power'] = 2
    # parameters['ema_m'] = 25
    # parameters['ema_m_phase'] = 100
    # parameters['ema_m_power'] = 3
    # parameters['sleep'] = 2
    # tasks_queue.put(parameters.copy())

    print('\r\nTotal tasks generated:', tasks_queue.qsize())


if __name__ == '__main__':

    tasks_queue = Queue()    # очередь заданий
    results_queue = Queue()  # очередь результаттов

    params = {
        # 'time_frames': {'5m': 300, '30m': 1800},
        'time_frames': {'1m': 60},
        'frame': '1m',
        'pair': 'USDT_TRX',
        'from': '2021-03-20 00:00:00',
        'to':   '2021-03-20 06:00:00',
    }

    print('press ctrl + q to interrupt safely')
    processors = 10
    done_tasks_hash_set = load_hash_list()
    data = Data(params)
    task_generator(params)
    initial_size = tasks_queue.qsize()
    bar = tqdm(total=initial_size, desc='Progress ', ncols=80)
    export = Exporter('reports/report.xlsx', 'test', save_interval=500)
    processes = do_multiprocessing(data)
    collecting_results(initial_size)

    for p in processes:
        p.join()
