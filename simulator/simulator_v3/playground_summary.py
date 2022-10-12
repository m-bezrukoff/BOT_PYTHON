from inc.inc_functions import percent, add_percent
from inc.inc_system import *


class Summary:
    def __init__(self, worker):
        self.printer = worker.printer
        self.data = worker.data
        self.params = worker.params
        self.frame = worker.params['frame']
        self.frame_size = worker.frame_size
        self.tradebook = worker.data.tradebook[self.data.tradebook_limiter:]
        self.points = worker.job.points[self.frame]
        self.positions = []
        self.result = {}

        self.calculate_positions()
        self.calcutale_total()

    def calculate_positions(self):
        position = {}
        is_position = False
        for i in self.tradebook:
            timestamp = i['date']

            if not is_position:
                if self.points['open'].get(timestamp):     # открываем позицию
                    is_position = True
                    position = dict()
                    position['timestamp_open'] = self.points['open'][timestamp]['trade_timestamp']
                    position['candle_timestamp'] = self.points['open'][timestamp]['candle_timestamp']
                    position['rate_open'] = add_percent(self.points['open'][timestamp]['y'], 0.05)
                    position['type'] = self.points['open'][timestamp]['type']
                    position['stoploss'] = self.points['open'][timestamp]['stoploss']
                    position['utc_date_open'] = self.points['open'][timestamp]['x']
            else:
                if self.points['close'].get(timestamp):     # закрываем позицию
                    is_position = False
                    position['timestamp_close'] = self.points['close'][timestamp]['trade_timestamp']
                    position['candle_timestamp'] = self.points['close'][timestamp]['candle_timestamp']
                    position['rate_close'] = self.points['close'][timestamp]['y']
                    position['utc_date_close'] = self.points['close'][timestamp]['x']
                    position['percent_profit'] = profit(position['rate_open'], position['rate_close'], 0.26, position['type'])
                    self.positions.append(position)
                else:
                    # if position['type'] == 'long' and i['rate'] > add_percent(position['rate_open'], 0.4):
                    #     is_position = False
                    #     position['timestamp_close'] = i
                    #     position['candle_timestamp'] = find_candle_start_time(timestamp, self.frame_size)
                    #     position['rate_close'] = add_percent(i['rate'], -0.05)
                    #     position['utc_date_close'] = utc_timestamp_to_date(position['candle_timestamp'])
                    #     position['percent_profit'] = profit(position['rate_open'], position['rate_close'], 0.26, position['type'])
                    #     self.positions.append(position)

                    if position['type'] == 'long' and i['rate'] < position['stoploss']:    # проверка на stoploss для long
                        is_position = False
                        position['timestamp_close'] = i['date']
                        position['candle_timestamp'] = find_candle_start_time(timestamp, self.frame_size)
                        position['rate_close'] = add_percent(i['rate'], -0.05)
                        position['utc_date_close'] = utc_timestamp_to_date(position['candle_timestamp'])
                        position['percent_profit'] = profit(position['rate_open'], position['rate_close'], 0.26, position['type'])
                        self.positions.append(position)

                    if position['type'] == 'short' and i['rate'] > position['stoploss']:    # проверка на stoploss для short
                        is_position = False
                        position['timestamp_close'] = i['date']
                        position['candle_timestamp'] = find_candle_start_time(timestamp, self.frame_size)
                        position['rate_close'] = add_percent(i['rate'], 0.05)
                        position['utc_date_close'] = utc_timestamp_to_date(position['candle_timestamp'])
                        position['percent_profit'] = profit(position['rate_open'], position['rate_close'], 0.26, position['type'])
                        self.positions.append(position)

    def calcutale_total(self):
        if self.printer:
            print(' ')
        percent_sum = 0
        total_positive = 0
        total_negative = 0
        initial_amount = 100
        final_amount = initial_amount

        for i in self.positions:
            percent_sum += i['percent_profit']
            final_amount = add_percent(final_amount, i['percent_profit'] * 1.4)
            if i['percent_profit'] > 0:
                total_positive += 1

            if i['percent_profit'] <= 0:
                total_negative += 1
            if self.printer:
                print('{} - {} {} {} {} ->: {}'.format(i['utc_date_open'], i['utc_date_close'], '\033[32m ' if i['percent_profit'] > 0 else '\033[31m', to2(i['percent_profit']), '%\033[0m', to2(final_amount)))
        if self.printer:
            print(' ')
        amount_sum = percent(initial_amount, final_amount)
        amount_sum_text = '+' + to2(amount_sum) if amount_sum > 0 else to2(amount_sum)
        percent_sum_text = '+' + to2(percent_sum) if percent_sum > 0 else to2(percent_sum)
        if self.printer:
            print('{}total percent: {} % real money: {} %{}'.format('\033[32m' if percent_sum > 0 else '\033[31m', percent_sum_text, amount_sum_text, '\033[0m'))
        try:
            wr = (total_positive / (total_positive + total_negative)) * 100
        except ZeroDivisionError:
            wr = 0
        if self.printer:
            print('total wins: {}   losts: {}    win ratio: {} %'.format(total_positive, total_negative, to2(wr)))
            print(' ')

        self.result = {
            'total_percent': round(percent_sum, 2),
            'total_money': round(amount_sum, 2),
            'wins': int(total_positive),
            'losses': int(total_negative),
            'ratio': round(wr, 2),
            'ema_f': self.params['ema_f'],
            'ema_f_phase': self.params['ema_f_phase'],
            'ema_f_power': self.params['ema_f_power'],
            'ema_m': self.params['ema_m'],
            'ema_m_phase': self.params['ema_m_phase'],
            'ema_m_power': self.params['ema_m_power'],
        }
        for attr in self.params:
            self.result[attr] = self.params[attr]


def profit(rate_in, rate_out, fee, typ):
    if typ == 'long':
        return percent(rate_in, rate_out) - fee
    elif typ == 'short':
        return -percent(rate_in, rate_out) - fee
    else:
        raise ValueError('type error in profit')
