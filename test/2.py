# -*- encoding: utf-8 -*-
import sys
from time import sleep

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import (QMainWindow, QApplication, QWidget,
                             QPushButton, QAction, QLineEdit, QMessageBox)


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = u'Тест'
        self.left = 200
        self.top = 200
        self.width = 400
        self.height = 140
        self.initUI()
        # self._closable = False

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.button = QPushButton(u'Закрыть', self)
        self.button.clicked.connect(self.on_click)
        self.show()

    # def closeEvent(self, evnt):
    #     if self._closable:
    #         super().closeEvent(evnt)
    #     else:
    #         evnt.ignore()

    def closeEvent(self, event):
        sleep(3)

        # reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
        #                              QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()

    @pyqtSlot()
    def on_click(self):
        self._closable = True
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())