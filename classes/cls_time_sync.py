import ntplib
import win32api
import datetime
from time import time


class TimeSync:
    def __init__(self, glob, log):
        self.glob = glob
        self.log = log
        self.ntp_client = ntplib.NTPClient()
        self.ntp_response = False
        self.sync_ntp_time()

    def sync_ntp_time(self):
        last_sync_ntp_time = self.glob.settings.get('last_sync_ntp_time')
        if last_sync_ntp_time:
            if self.glob.settings['last_sync_ntp_time'] - time() < 21600:
                return None

        for i in range(5):
            try:
                self.ntp_response = self.ntp_client.request('pool.ntp.org')
                break
            except Exception:
                pass

        if self.ntp_response:
            t1 = datetime.datetime.now()
            utc_time = datetime.datetime.utcfromtimestamp(self.ntp_response.tx_time)
            win32api.SetSystemTime(
                utc_time.year,
                utc_time.month,
                utc_time.weekday(),
                utc_time.day,
                utc_time.hour,
                utc_time.minute,
                utc_time.second,
                int(utc_time.microsecond / 1000))

            print(f'time before update {time_format(t1)}')
            print(f'time after update {time_format(datetime.datetime.now())}')

            self.glob.settings['last_sync_ntp_time'] = time()
            self.glob.save_settings()

        else:
            print('Time sync failed')


def time_format(date):
    return date.strftime('%Y.%m.%d %H:%M:%S.%f')[:-3]
