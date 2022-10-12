import plotly.offline as po
import plotly.graph_objs as go
from time import sleep
from random import randint
from threading import Thread
from PyQt5.Qt import QThread

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5 import QtCore, QtWidgets
import sys


def show_qt(fig):
    raw_html = '<html><head><meta charset="utf-8" />'
    raw_html += '<script src="https://cdn.plot.ly/plotly-latest.min.js"></script></head>'
    raw_html += '<body>'
    raw_html += po.plot(fig, include_plotlyjs=False, output_type='div')
    raw_html += '</body></html>'

    fig_view = QWebEngineView()
    # setHtml has a 2MB size limit, need to switch to setUrl on tmp file
    # for large figures.
    fig_view.setHtml(raw_html)
    fig_view.show()
    fig_view.raise_()
    return fig_view


def do_it():
    while True:
        y = [randint(1, 10) for i in range(10)]
        fig = go.Figure(data=[{'type': 'scattergl', 'y': y}])
        fig_view = show_qt(fig)
        sleep(10)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    t = Thread(target=do_it, name='show_qt')
    t.start()
    # self.glob.thread_list.append(t)
    # t.daemon = True

    sys.exit(app.exec_())