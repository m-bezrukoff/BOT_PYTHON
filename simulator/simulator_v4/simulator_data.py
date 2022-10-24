import os
from inc.inc_system import *
from classes.cls_file_io import FileIO


class Data:
    def __init__(self, parameters):
        self.io = FileIO()
        self.params = parameters
        self.pair = parameters['pair']
        self.from_timestamp = utc_date_to_timestamp(parameters['from'])
        self.to_timestamp = utc_date_to_timestamp(parameters['to'])
        self.tradebook = self.tradebook_loader()
        self.total_trades = len(self.tradebook)

    def tradebook_loader(self):
        _hash = md5_hash(self.pair + str(self.from_timestamp) + str(self.to_timestamp))
        cache_tradebook_file = '../save/_cache_' + self.pair + '_' + _hash + '.dat'
        if os.path.isfile(cache_tradebook_file):
            tradebook = self.io.load_zipped_file(cache_tradebook_file)
        else:
            tradebook_file = '../save/' + self.pair + '_tradebook.dat'
            tradebook = self.io.load_zipped_file(tradebook_file)
            tradebook = [i for i in tradebook if self.to_timestamp > i['date'] > self.from_timestamp]
            self.io.save_zipped_file(cache_tradebook_file, tradebook)
        return tradebook
