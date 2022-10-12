from simulator_v2.playground_data import Data
from simulator_v2.playground_multiprocessor import MultiProcessorRender
from simulator_v2.playground_summary import Summary
from inc.inc_system import *
from multiprocessing import cpu_count, Queue
from tqdm import tqdm
import hashlib


class Worker:
    def __init__(self, params):
        self.results_queue = Queue()
        self.processes_list = []
        self.params = params
        self.data = Data(self.params)
        self.trades_total = len(self.data.tradebook)
        self.processes = self.calculate_threads_number()
        self.periods = self.generate_splitted_periods()
        self.tasks = self.generate_tasks()
        self.result = []
        self.graphics_data = {}
        self.print_info()

    def calculate_threads_number(self):
        if self.params['threads']:
            return self.params['threads']
        c = int(self.trades_total / 4000)
        return c if c < cpu_count() else cpu_count()

    def generate_splitted_periods(self):
        step = self.data.total_trades // self.processes
        max_timeframe = max(self.data.params['time_frames'].values())
        half = max_timeframe // 2  # половина минимального таймфрейма
        tb = self.data.tradebook
        num_borders = [n * step for n in range(self.processes)][1:]  # намеченные делители по кол-ву
        time_borders = [tm for m in num_borders for tm in range(tb[m]['date'] - half, tb[m]['date'] + half) if tm % max_timeframe == 0]
        time_borders.insert(0, tb[0]['date'])
        time_borders.append(tb[-1]['date'])
        periods = [[time_borders[x], time_borders[x + 1]] for x in range(len(time_borders) - 1)]
        print(periods)
        return periods

    def generate_tasks(self):
        charts = []
        tradebook = []
        frame = self.params['frame']
        print('original charts', self.data.charts[frame][0]['timestamp'], '-', self.data.charts[frame][-1]['timestamp'])

        for period in self.periods:
            tradebook.append([i for i in self.data.tradebook if period[1] > i['date'] >= period[0]])

        # для charts делаем отступ на максимальный параметр индикаторов, чтобы были прорисованы все индикаторы в периоде
        for period in self.periods:
            c = {}
            for frame in self.params['time_frames']:
                fr = find_candle_start_time(period[0] - (self.data.params['time_frames'][frame] * self.data.indicators_margin), frame)
                to = find_candle_start_time(period[0], frame)      # от отступа до первого трейда
                c[frame] = [candle for candle in self.data.charts[frame] if to > candle['timestamp'] >= fr]
            charts.append(c)

        return [{'charts': charts[i], 'tradebook': tradebook[i], 'period': self.periods[i], 'params': self.data.params} for i in range(len(self.periods))]

    def print_info(self):
        frame = self.params['frame']
        print('time_frames', self.params['time_frames'])
        print('margin:', self.data.indicators_margin, 'from_margined:', self.data.from_margined)
        print('from time:', self.data.from_timestamp, ' - ', self.params['from'])
        print('to time:  ', self.data.to_timestamp, ' - ', self.params['to'])
        print('')
        print('first trade time:', self.data.tradebook[0]['date'], utc_timestamp_to_date(self.data.tradebook[0]['date']))
        print('last  trade time:', self.data.tradebook[-1]['date'], utc_timestamp_to_date(self.data.tradebook[-1]['date']))
        print('')
        print('first candle time:', self.data.charts[frame][0]['timestamp'], utc_timestamp_to_date(self.data.charts[frame][0]['timestamp']))
        print('last  candle time:', self.data.charts[frame][-1]['timestamp'], utc_timestamp_to_date(self.data.charts[frame][-1]['timestamp']))
        print('')
        print('trades total:', self.trades_total)
        print('')

    def do_multiprocessing(self):
        print('\r\nCalculating in {} threads ...'.format(self.processes))
        for i in range(len(self.tasks)):
            process = MultiProcessorRender(self.tasks[i], i, self.results_queue)
            self.processes_list.append(process)

    def collecting_results(self):
        while self.results_queue.empty():
            sleep(0.001)

        stop = 0
        bar = tqdm(total=((self.data.to_timestamp - self.data.from_timestamp) // 300), desc='Progress ', ncols=80)
        while True:
            if not self.results_queue.empty():
                x = self.results_queue.get()
                bar.update(1)
                if x == 'stop':
                    stop += 1
                    if stop == len(self.processes_list) and self.results_queue.empty():
                        break
                else:
                    self.result.append(x)
        bar.close()
        self.result = sorted(self.result, key=lambda k: k['timestamp'])
        print('Finished all processes. Total candles', len(self.result))

    def format_graphics_data(self):
        self.graphics_data['pair'] = self.params['pair']
        self.graphics_data['timestamps'] = [i['chart']['timestamp'] for i in self.result]
        self.graphics_data['utc_dates'] = [i['chart']['utc_date'] for i in self.result]
        self.graphics_data['charts_open'] = [i['chart']['open'] for i in self.result]
        self.graphics_data['charts_close'] = [i['chart']['close'] for i in self.result]
        self.graphics_data['charts_high'] = [i['chart']['high'] for i in self.result]
        self.graphics_data['charts_low'] = [i['chart']['low'] for i in self.result]
        self.graphics_data['amplitude'] = [i['chart']['amplitude'] for i in self.result]

        self.graphics_data['points_open'] = {
            'x': [i['points_open']['x'] for i in self.result if i['points_open']],
            'y': [i['points_open']['y'] for i in self.result if i['points_open']],
            'marker': [i['points_open']['marker'] for i in self.result if i['points_open']],
        }

        self.graphics_data['points_close'] = {
            'x': [i['points_close']['x'] for i in self.result if i['points_close']],
            'y': [i['points_close']['y'] for i in self.result if i['points_close']],
            'marker': [i['points_close']['marker'] for i in self.result if i['points_close']],
        }

        for att in self.result[0]['arr'].keys():
            self.graphics_data[att] = [i['arr'][att] for i in self.result]

        for i in range(len(self.graphics_data['timestamps'])-1):
            if self.graphics_data['timestamps'][i] + self.params['time_frames'][self.params['frame']] != self.graphics_data['timestamps'][i+1]:
                raise ValueError('ERROR', self.graphics_data['timestamps'][i], self.graphics_data['timestamps'][i+1])


def load_hash_file():
    try:
        _file = open('reports/hash.txt', 'r+')
        _set = set(_file.read().split('\n'))
        print('hash list size:', len(_set))
        _file.close()
        return _set

    except Exception:
        _file = open('reports/hash.txt', 'a+')
        _file.close()
        return set()


def save_hash_file(_hash):
    _file = open('reports/hash.txt', 'a')
    _file.write(_hash + '\n')
    _file.close()


def make_hash(par):
    h = hashlib.md5(str(par).encode())
    return h.hexdigest()


if __name__ == '__main__':
    hash_list = load_hash_file()

    params = {
        'threads': 8,
        # 'time_frames': {'5m': 300, '30m': 1800},
        'time_frames': {'5m': 300},
        'frame': '5m',
        # 'time_frames': {'30m': 1800},
        # 'time_frames': {'1m': 60},
        # 'frame': '1m',

        'pair': 'USDT_TRX',
        'from': '2021-03-01 00:00:00',
        'to': '2021-03-11 00:00:00',

        'bb': 16,
        'bb_dev': 2,

        'ema_f': 9,
        'ema_f_power': 2,
        'ema_f_phase': 100,

        'ema_m': 15,
        'ema_m_power': 2,
        'ema_m_phase': 100,

        'ema_s': 100,
        'ema_xs': 200,
    }

    for ema_f in range(5, 30, 2):
        for ema_m in range(7, 35, 2):
            if ema_f < ema_m:
                params['ema_f'] = ema_f
                params['ema_m'] = ema_m
                # params['ema_f_phase'] = ema_f_phase
                # params['ema_f_power'] = ema_f_power
                # params['ema_m_phase'] = ema_m_phase
                # params['ema_m_power'] = ema_m_power
                _hash = make_hash(params)
                print('hash:', _hash)
                if _hash not in hash_list:
                    t10 = time()
                    w = Worker(params)
                    w.do_multiprocessing()
                    w.collecting_results()
                    r = Summary(w)
                    r.save_xls_results()
                    print('total time spent:', to2(time() - t10), 'sec')
                    print('--------------------------------------------\r\n')
                    save_hash_file(_hash)
                    hash_list.add(_hash)
