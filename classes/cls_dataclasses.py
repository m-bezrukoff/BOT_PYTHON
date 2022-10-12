from dataclasses import dataclass
from typing import Any, Literal
from classes.cls_pipe import MyPipe


@dataclass
class PublicTradeData:
    """ Структура данных публичного трейда.
        Не используем globalTradeID, orderNumber на Poloniex """
    date: int
    id: int
    type: int
    rate: float
    amount: float


class SendMsg:
    """ Отправка сообщения в pipe_main, pipe_pair """
    def __init__(self,
                 pipe: MyPipe,
                 action: str,
                 pair: str = None,
                 data: Any = None):
        self.action = action
        self.pair = pair
        self.data = data
        pipe.a.send(self.__dict__)


class ReceiveMsg:
    """ Получение сообщения в pipe_main, pipe_pair """
    def __init__(self, pipe: MyPipe):
        msg = pipe.b.recv()
        self.action = msg['action']
        self.pair = msg['pair']
        self.data = msg['data']
        self.run()

    def run(self):
        return self


class SendApiMsg:
    """ Отправка сообщения в pipe_api """
    def __init__(self,
                 pipe: MyPipe,
                 action: str,
                 reply: Literal['pipe_main', 'pipe_pair', 'pipe_log'],
                 pair: str = None):
        self.action = action
        self.reply = reply
        self.pair = pair
        pipe.a.send(self.__dict__)


class ReceiveApiMsg:
    """ Получение сообщения в объекте Api """
    def __init__(self, pipe: MyPipe):
        msg = pipe.b.recv()
        self.action = msg['action']
        self.reply = msg.get('reply')
        self.pair = msg.get('pair')
        self.run()

    def run(self):
        return self

