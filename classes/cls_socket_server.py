from websocket_server import WebsocketServer
from classes.cls_system import System
from json import dumps, loads


class SocketServer(System):     # Локальный сокет сервер + экспорт json данных для внешней графики
    def __init__(self, glob, log):
        super().__init__()
        self.glob = glob
        # self.pair = self.glob.display_pair
        self.log = log

        self.port = 8889
        self.server = WebsocketServer(port=self.port)
        self.server.set_fn_new_client(self.on_new_client)
        self.server.set_fn_client_left(self.on_client_left)
        self.server.set_fn_message_received(self.on_message_received)

    def on_new_client(self, client, server):
        print('Client {} connected address: {}'.format(client['id'], client['address']))

    def on_client_left(self, client, server):
        pass
        #   self.log.error('Client {} disconnected'.format(client['id']))

    def on_message_received(self, client, server, message):
        # print("------------------------ Client(%d) said: %s" % (client['id'], message))
        dat = loads(message)
        # print(dat['display_timeframe'])
        self.glob.display_timeframe = dat['display_timeframe']

    def send(self, msg):
        # print(dumps(msg))
        self.server.send_message_to_all(dumps(msg))

    def run(self):
        self.server.run_forever()

    def close(self):
        self.server.shutdown()
