import os
from inc.inc_system import *
from classes.cls_file_io import FileIO


class Data:
    def __init__(self, parameters):
        self.io = FileIO()
        self.params = parameters
        self.pair = parameters['pair']
        self.frame = parameters['frame']
        self.from_timestamp = utc_date_to_timestamp(parameters['from'])
        self.to_timestamp = utc_date_to_timestamp(parameters['to'])

        self.time_update_charts = 0
        self.time_update_indicators = 0
        self.margin = 300       # отсуп свечей для рассчета индикаторов
        self.time_margin = {x: self.from_timestamp - self.margin * self.params['time_frames'][x] for x in self.params['time_frames']}   # отступ секунд для рассчета индикаторов

        self.cache = {x: {} for x in self.params['time_frames']}
        self.added_candles = {x: 0 for x in self.params['time_frames']}   # кол-во всех добавленных свечей за один трейд
        self.timestamp = 0
        # self.tradebook_limiter = 0 if not tradebook else limiter  # граница отступа от перебираемого диапазона
        self.tradebook_limiter = 0

        self.tradebook = self.tradebook_loader()
        self.total_trades = len(self.tradebook)

    def tradebook_loader(self):
        _hash = md5_hash(self.pair + str(self.from_timestamp) + str(self.to_timestamp) + str(self.params['time_frames']))
        cache_tradebook_file = '../save/_cache_' + self.pair + '_' + _hash + '.dat'
        if os.path.isfile(cache_tradebook_file):
            tradebook = self.io.load_zipped_file(cache_tradebook_file)
        else:
            tradebook_file = '../save/' + self.pair + '_tradebook.dat'
            tradebook = self.io.load_zipped_file(tradebook_file)
            margined_from = self.from_timestamp - max(self.params['time_frames'].values()) * self.margin
            # загружаем всегда с большим отступом слева, для гаранатированного расчета ema с большим периодом
            tradebook = [i for i in tradebook if self.to_timestamp > i['date'] >= margined_from]
            self.io.save_zipped_file(cache_tradebook_file, tradebook)
        return tradebook
