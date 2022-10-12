from inc.inc_system import join_args, save_file, save_pickle
from config import *


class Log:

    def __init__(self):
        super().__init__()
        self.buffer_pair = {pair: [] for pair in conf_pairs}

    def log(self, pair, *args):
        print(pair, join_args(args))
