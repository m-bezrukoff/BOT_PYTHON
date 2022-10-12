# -*- coding: utf-8 -*-
from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QThread
from config import *
from traceback import format_exc
from classes.cls_file_io import FileIO
from threading import Thread
from classes.cls_dataclasses import ReceiveMsg
from inc.inc_system import join_args


class Log(QThread, FileIO):
    log_signal = pyqtSignal(str, str)

    def __init__(self, pipe_log):
        super().__init__()
        self.pipe_log = pipe_log
        self.logs_profile = get_logs_profile()
        self.buffer = {i: list() for i in self.logs_profile}

        self.communicator_thread = Thread(target=self.run, name=f'log_thread')
        self.communicator_thread.start()
        print('Log thread listening for requests')

    def run(self):
        while True:
            msg = ReceiveMsg(self.pipe_log)
            if msg.action == 'exit':
                print('closing Log thread')
                break
            else:
                getattr(self, msg.action)(msg.pair, msg.data)

    def log(self, pair, msg):
        msg = timed_msg(msg)
        print(msg)
        if self.logs_profile[pair]:
            self.buffer[pair].append(msg)
        self.log_signal.emit(msg, pair)

    def private_trades(self, msg):
        msg = timed_msg(msg)
        if self.logs_profile['private_trades']:
            self.buffer['private_trades'].append(msg)
        self.log_signal.emit(msg, 'trades')

    def socket(self, *args):
        msg = timed_msg(args)
        if self.logs_profile['socket']:
            self.buffer['socket'].append(msg)
        self.log_signal.emit(msg, 'socket')

    def error(self, *args):
        msg = timed_msg(args)
        if self.logs_profile['error']:
            self.buffer['error'].append(msg)
        self.log_signal.emit(msg, 'error')

    def error_trace(self, *args):
        msg = timed_msg(args)
        if self.logs_profile['error']:
            self.buffer['error'].append(msg)
            self.buffer['error'].append(format_exc())
        self.log_signal.emit(msg, 'error')

    def requests(self, *args):
        msg = timed_msg(args)
        if self.logs_profile['request']:
            self.buffer['request'].append(msg)
        print(msg)
        self.log_signal.emit(msg, 'request')

    def save_logs(self):
        for i in self.logs_profile:
            if self.logs_profile[i]:
                ln = len(self.buffer[i])
                if ln > 0:
                    self.save_file_multiline('log/log_' + i + '.txt', self.buffer[i][:ln])
                    self.buffer[i] = self.buffer[i][ln:]


def timed_msg(*args):
    return datetime.now().strftime('%d.%m %H:%M:%S.%f')[:-3] + ' ' + join_args(args)


def get_logs_profile():
    profile = {i: True if conf_save_logs[i] else False for i in conf_save_logs if i != 'pairs'}
    for i in conf_pairs:
        profile[i] = True if conf_save_logs['pairs'] else False
    return profile
