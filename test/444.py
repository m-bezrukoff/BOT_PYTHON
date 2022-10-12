from urllib.request import urlopen

# Для быстрого запуска лучше заменить на абсолютные импорты
from PyQt5.Qt import *


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    import traceback
    text += ''.join(traceback.format_tb(tb))

    print(text)
    QMessageBox.critical(None, 'Error', text)
    quit()


import sys
sys.excepthook = log_uncaught_exceptions


class MyCheckUrlThread(QThread):
    about_check_url = pyqtSignal(str)

    def __init__(self, urls):
        super().__init__()

        self.urls = urls

    def run(self):
        for url in self.urls:
            try:
                code = urlopen(url).getcode()
            except Exception as e:
                # Пусть будет исключение
                code = str(e)

            self.about_check_url.emit('{}------{}'.format(url, code))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.urls = QTextEdit()
        self.urls.setText("""\
https://ru.stackoverflow.com
https://ru.stackoverflow.com/questions/893436/
https://google.com
http://ya.ru
http://not_found_site.123
""")

        self.result = QTextBrowser()

        self.pb_check = QPushButton('Check')
        self.pb_check.clicked.connect(self._on_click_check)

        layout = QHBoxLayout()
        layout.addWidget(self.urls)
        layout.addWidget(self.result)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.pb_check)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.thread = MyCheckUrlThread(urls=None)
        self.thread.about_check_url.connect(self._on_about_check_url)

    def _on_click_check(self):
        urls = self.urls.toPlainText().strip().split('\n')

        self.thread.urls = urls
        self.thread.start()

    def _on_about_check_url(self, text):
        self.result.append(text)


if __name__ == "__main__":
    app = QApplication([])

    mw = MainWindow()
    mw.show()

    app.exec()
