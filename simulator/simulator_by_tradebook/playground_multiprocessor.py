from simulator_v2.playground_indicators import Indicators
from simulator_v2.playground_data import Data
from simulator_v2.playground_enter_points import *
from multiprocessing import Process


class MultiProcessorRender:
    def __init__(self, task, task_number, results_queue):
        self.results_queue = results_queue
        self.task_number = task_number
        self.params = task['params']
        self.period = task['period']

        self.data = Data(task['params'], task['charts'], task['tradebook'])

        self.charts = self.data.charts
        self.tradebook = self.data.tradebook
        self.indicators = Indicators(self.data)
        self.job = Job(self.indicators)
        self.points = self.job.points
        self.p = Process(target=self.run, args=())
        self.p.start()

    def run(self):
        for i in self.tradebook:
            self.data.update_charts(int(i['date']), float(i['rate']), float(i['amount']), i['type'])
            self.indicators.incremental_indicators_update()
            self.job.run(i['date'])
            self.export()
        self.export(last_candle=True)
        self.results_queue.put('stop')

    def export(self, last_candle=False):
        def get_position(_charts, _timestamp):
            for i in range(-1, -len(_charts), -1):
                if _charts[i]['timestamp'] == _timestamp:
                    return i
            raise ValueError('get_position -> TIMESTAMP NOT FOUND')

        frame = self.data.frame
        if self.data.charts_export[frame] or last_candle:
            timestamp = self.data.charts_export[frame].pop() if not last_candle else self.charts[frame][-1]['timestamp']
            position = get_position(self.charts[frame], timestamp)

            res = {
                'arr': {att: self.indicators.arr[frame][att][position] for att in self.indicators.arr[frame].keys()},
                'timestamp': timestamp,
                'chart': self.charts[frame][position],
                'points_open': self.points[frame]['open'].get(timestamp),
                'points_close': self.points[frame]['close'].get(timestamp)
            }
            self.results_queue.put(res)
