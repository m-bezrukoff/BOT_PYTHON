from config import *
from multiprocessing import Pipe, Process, current_process, Lock, active_children
from time import sleep
from inc.inc_functions import split
from threading import Thread, currentThread
from classes.cls_pair_thread import PairThread


class PairsMultiprocessing:
    def __init__(self, glob, log, lock, pipe_pair, pipe_main, pipe_log, pairs, balances):
        self.log = log
        self.processes = []
        self.distribution = split(list(conf_pairs), processes)
        self.do_multiprocessing(glob, lock, pipe_pair, pipe_main, pipe_log, pairs, balances)

    def do_multiprocessing(self, glob, lock, pipe_pair, pipe_main, pipe_log, pairs, balances):
        for pair_list in self.distribution:
            if len(pair_list) > 0:
                process = Process(target=process_worker, args=(glob.data, lock, pair_list, pipe_pair, pipe_main, pipe_log, pairs.data, balances.data))
                process.start()


def process_worker(glob_data, lock, pair_list, pipe_pair, pipe_main, pipe_log, pairs_data, balances_data):
    lock.acquire()
    print(current_process(), 'of', pair_list)
    lock.release()

    pair_threads = [Thread(target=subprocess_thread_worker, name=f'{pair}_thread', args=(
        pair,
        glob_data,
        lock,
        pipe_pair[pair],
        pipe_main,
        pipe_log,
        pairs_data,
        balances_data
    )) for pair in pair_list]

    for thread in pair_threads:
        thread.start()


def subprocess_thread_worker(pair, glob_data, lock, pipe_pair, pipe_main, pipe_log, pairs_data, balances_data):
    pair_thread = PairThread(pair, glob_data, lock, pipe_pair, pipe_main, pipe_log, pairs_data, pairs_data[pair], balances_data)
