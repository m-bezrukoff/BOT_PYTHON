from time import time, sleep, gmtime, strftime, mktime, timezone, strptime, localtime
from config import *
import hashlib


def utc_timestamp_to_date(t=None):
    #   from timestamp to utc date string
    return strftime('%Y-%m-%d %H:%M:%S', gmtime(t))


def local_timestamp_to_date():
    #   from timestamp to utc date string
    return strftime('%H:%M:%S', localtime())


def utc_date_to_timestamp(date: str) -> int:
    """ from date string to timestamp. input: '2018-10-22 15:03:57' """
    return int(mktime(strptime(date, '%Y-%m-%d %H:%M:%S'))) - timezone


def find_first_candle_time():
    return int(time() - max(conf_time_frames.values()) * conf_total_candles)


def find_candle_start_time(timestamp: int, frame_size: int):
    # size = conf_time_frames[frame]
    return int((timestamp // frame_size) * frame_size)


def find_candle_start_by_candles_ago(candles, frame):
    return int(((time() - frame * candles) // frame) * frame)


def to16(_):
    return format(_, '.16f')


def to6(_):
    return format(_, '.06f')


def to8(_):
    return format(_, '.08f')


def to2(_):
    return format(_, '.02f')


def to4(_):
    return format(_, '.04f')


def to0(_):
    return format(_, '.00f')


def ro8(_):
    return round(_, 8)


def ro2(_):
    return round(_, 2)


def to_fixed(num, digits=0):
    return f"{num:.{digits}f}"


def time_multiple(period, shift=0):
    if round((time()) - shift) % period == 0:
        return True
    else:
        return False


def show_taken_time(fn):
    def wrapped(*args, **kwargs):
        start_time = time()
        res = fn(*args, **kwargs)
        print(f'время выполнения {fn.__name__} : {to4(time() - start_time)} c')
        return res
    return wrapped


def rotation_delay(fn):
    def wrapped(*args, **kwargs):
        start_time = time()
        res = fn(*args, **kwargs)
        dif = time() - start_time
        if dif < conf_pairs_rotation_delay:
            wait_time = conf_pairs_rotation_delay - dif
            sleep(wait_time)
        return res
    return wrapped


def join_args(args):
    return ''.join(map(lambda x: ' ' + str(x), args))


def md5_hash(data):
    h = hashlib.md5(str(data).encode())
    return h.hexdigest()
