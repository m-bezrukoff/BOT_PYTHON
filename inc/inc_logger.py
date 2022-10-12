from logging import FileHandler
import sys


def get_logger(file, name=__file__, encoding='utf-8'):
    import logging
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)

    # Будут строки вида: "[2017-08-23 09:54:55,356] main_v4.py:34 DEBUG    foo"
    # formatter = logging.Formatter('[%(asctime)s] %(filename)s:%(lineno)d %(levelname)-8s %(message)s')
    formatter = logging.Formatter('%(message)s')

    # В файл
    fh = FileHandler(file, encoding=encoding)
    fh.setFormatter(formatter)
    log.addHandler(fh)

    # В stdout
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(formatter)
    log.addHandler(sh)

    return log
