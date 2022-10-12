# -*- coding: utf-8 -*-
from inc.inc_system import join_args
from classes.cls_dataclasses import SendMsg
from traceback import format_exc


class LogInsideProcess:
    def __init__(self, pipe_log, pair):
        self.pipe_log = pipe_log
        self.pair = pair

    def log(self, msg):
        SendMsg(pipe=self.pipe_log, action='log', pair=self.pair, data=msg)

    def private_trades(self, msg):
        SendMsg(pipe=self.pipe_log, action='private_trades', pair=self.pair, data=msg)

    def error(self, *args):
        SendMsg(pipe=self.pipe_log, action='error', pair=self.pair, data=join_args(args))

    def error_trace(self, *args):
        SendMsg(pipe=self.pipe_log, action='error_trace', pair=self.pair, data=join_args(args) + format_exc())
