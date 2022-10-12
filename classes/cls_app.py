from PyQt6.QtWidgets import QTabWidget, QMainWindow, QVBoxLayout, QWidget, QPlainTextEdit, QSplitter, QHBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6 import QtGui, QtCore
from PyQt6.QtCore import QUrl, Qt
from config import *
from inc.inc_system import sleep
from classes.cls_dataclasses import SendMsg

from multiprocessing import Pipe, Process, current_process, Lock, active_children


class App(QMainWindow):
    def __init__(self, glob, log, pipe_pair, pipe_log, pipe_api, pipe_socket):
        super().__init__()
        self.glob = glob
        self.log = log
        self.pipe_pair = pipe_pair
        self.pipe_log = pipe_log
        self.pipe_api = pipe_api
        self.pipe_socket = pipe_socket

        self.tab = {}
        self.log_box = {}
        self.setWindowIcon(QtGui.QIcon('inc/icon.png'))
        self.setWindowTitle('MaxB Poloniex Trader')
        self.height_ratio = 0.7
        self.resize(1400, 1000)
        self.tab_widget = QTabWidget()
        self.tab_widget.setCurrentIndex(0)
        self.tab_widget.tabBarClicked['int'].connect(self.on_tab_click)
        self.setStyleSheet('QPlainTextEdit {background-color:#262626; color:#cccccc; border:1px solid #111111; font-size:14px; font-family:"Consolas"}')

        for name in list([pair for pair in conf_pairs]) + ['error', 'socket', 'request', 'trades']:
            self.tab[name] = QWidget()
            self.tab_widget.addTab(self.tab[name], name.upper())
            self.log_box[name] = QPlainTextEdit()
            self.log_box[name].setReadOnly(True)
            self.log_box[name].setMaximumBlockCount(1000)
            self.log_box[name].verticalScrollBar().setValue(self.log_box[name].verticalScrollBar().maximum())
            v_box = QVBoxLayout(self.tab[name])
            v_box.addWidget(self.log_box[name])

        self.web_widget = QWebEngineView()
        # self.web_widget.load(QUrl(self.glob.script_path + '/graphics/plotly.html'))
        self.web_widget.setGeometry(QtCore.QRect(0, 0, 1400, int(1000 * self.height_ratio)))
        self.web_widget.show()

        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.addWidget(self.web_widget)
        self.splitter.addWidget(self.tab_widget)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.splitter)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.hbox)

        self.central_widget = QWidget()
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.log.log_signal.connect(self.gui_log)

    def on_tab_click(self, num):
        if num < len(conf_pairs):
            self.glob.display_pair = list(conf_pairs.keys())[num]

    def gui_log(self, msg, where):
        self.log_box[where].appendPlainText(msg)

    def closeEvent(self, event):

        active_processes = active_children()
        for i in active_processes:
            i.kill()

        self.api_socket.close()
        # self.glob.data['stop_by']['closeApp'] = True
        for pair in conf_pairs:
            SendMsg(self.pipe_pair[pair], 'exit')

        SendMsg(self.pipe_api, 'exit')  # цепная остановка потоков http api


        # self.socket_server.close()
        # self.session.save_session()
        # for pair in conf_pairs:
        #     self.public_trades[pair].shutdown() # перенести в pipe
        SendMsg(self.pipe_log, 'exit')
        self.log.save_logs()
