class TacticBuy:
    def __init__(self, pair, glob, api, pairs, public_orders, public_trades, charts, coins, orders, sessions, indicators, private_trades, log):
        super().__init__(pair, glob, api, pairs, charts, sessions, indicators, log)
        self.pair = pair
        self.glob = glob
        self.api = api
        self.coins = coins
        self.log = log
        self.pairs = pairs[pair]
        self.public_orders = public_orders[pair]
        self.public_trades = public_trades[pair]
        self.charts = charts[pair]
        self.orders = orders[pair]
        self.private_trades = private_trades[pair]
        self.sessions = sessions[pair]
        self.indicators = indicators[pair]


# def tactic_buy(get):
#     for i in range(len(charts[get].data)):
#
#
#         # #8 провал на 1 свече
#         score += collapse_one_candle(get, i)
#         comment += '#8: падение на одной свече '

        # print('{} SMA: {} EMA: {} STOCH: {}% MACD: {} RSI: {}%'.format(printable_time(),
        #                                                              to8(SMA(get)[-1]),
        #                                                              to8(EMA(get)[-1]),
        #                                                              to2(STOCH(get, 'K')[-1]),
        #                                                              to8(MACD(get, 'H')[-1]),
        #                                                              to2(RSI(get)[-1])))
        # print('{} MACD: {} Signal: {} Histogram: {}'.format(printable_time(),
        #                                                     to8(MACD(get, 'M')[-1]),
        #                                                     to8(MACD(get, 'S')[-1]),
        #                                                     to8(MACD(get, 'H')[-1])))
        # print('M: ', MACD(get, 'M')[-1])
        # print('S: ', MACD(get, 'S')[-1])
        # print('H: ', MACD(get, 'H')[-1])
        # rate_dynamic(get, 3, 1)
        # rate_dynamic_2h(get, 3, 1)
        # vol_dynamic_5m(get, 3, 1)
        # print('SMA', SMA(get, 'close', 21))
        # print('EMA', EMA(get, 'close', 7))
        # print('MACD', MACD(get, 'close', 12, 26, 9))
        # print('RSI', RSI(get, 'close', 14))
        # print('STOCH', STOCH(get))
        #
        # if time_multiple(20):
        #     do_request.update_chart(get)


        # print('{} score: {}'.format(comment, to2(score)))

        # print('{} стох:{}% macd:{} Приближение SAR:{}% mom:{}%'
        #       .format(utc_timestamp_to_date(charts[get].data[i]['timestamp']),
        #               to0(stoch_k[i]),
        #               to8(macdhist[i]),
        #               to2(percent(charts[get].data[i]['open'], sar[i])),
        #               to2(mom[i]*100000)))

        # # #1 macd откат с минимума
        # if (macdhist[i] != 'nan') and (macdhist[i - 1] != 'nan') and (macdhist[i - 2] != 'nan'):
        #     if (macdhist[i] > macdhist[i - 1]) and (macdhist[i - 1] <= macdhist[i - 2]):
        #         if -0.00000600 < macdhist[i] < 0:
        #             score += 0.2
        #             comment = comment + '#1: 0.2 '
        #
        #         if -0.00001000 < macdhist[i] < -0.00000600:
        #             score += 0.3
        #             comment = comment + '#1: 0.6 '
        #
        #         if -0.00002000 < macdhist[i] < -0.00001000:
        #             score += 0.7
        #             comment = comment + '#1: 0.9 '
        #
        #         if -0.00003000 < macdhist[i] < -0.00002000:
        #             score += 1.2
        #             comment = comment + '#1: 1.2 '
        #
        #         if macdhist[i] < -0.00003000:
        #             score += 1.3
        #             comment = comment + '#1: 1.3 '

        # if (osma[i] != 'nan') and (osma[i - 1] != 'nan') and (osma[i - 2] != 'nan'):
        #     if osma[i] < 0:
        #         if (abs(osma[i]) > abs(macdsignal[i])) and (abs(osma[i - 1]) <= abs(macdsignal[i - 1])):
        #             score += 0.9
        #             comment = comment + '#1: 0.2 '
        #
        # # #2 macd переход из отрицательной зоны в положительную
        # if (macdhist[i] != 'nan') and (macdhist[i - 1] != 'nan'):
        #     if (macdhist[i] > 0) and (macdhist[i - 1] <= 0):
        #         score += 0.8
        #         comment = comment + '#2: 0.5 '
        #
        # # #3 приветсвуем отрицательный macd
        # if macdhist[i] != 'nan':
        #     if macdhist[i] <= 0:
        #         score += 0.1
        #         comment = comment + '#3: 0.1 '
        #     else:
        #         score -= 0.3
        #         comment = comment + '#3: -0.3 '
        #

        #
        # # #5 разворот параболика с падающего на растущий
        # if (sar[i-1] != 'nan') and (sar[i] != 'nan'):
        #     if (sar[i-1] >= charts[get].data[i-1]['open']) and (sar[i] < charts[get].data[i]['open']):
        #         score += 0.5
        #         comment = comment + '#5: 0.5 '
        #
        # # #6 свеча сильно ушла наверх
        # if charts[get].data[i-1] and charts[get].data[i]:
        #     if percent(charts[get].data[i-1]['close'], charts[get].data[i]['open']) > 0.1:
        #         score -= 0.3
        #         comment = comment + '#6: -0.3 '
        #
        # # #7 скользящая переход из падения в рост
        # if (macd[i] != 'nan') and (macd[i - 1] != 'nan') and (macd[i - 2] != 'nan'):
        #     if macd[i-2] > macd[i-1] < macd[i]:
        #         score += 0.4
        #         comment = comment + '#7: 0.4 '

# def stochastic_min(pair):
#     # приветствуем минимальный стохастик
#     score = round(-0.03 * int(indicators[pair].stoch[-1]) + 1, 2)
#     comment = 'стохастик: {} % score: {}'.format(round(indicators[pair].stoch[-1]), score)
#     return {'score': score, 'comment': comment}


# def collapse_one_candle(pair, threshold=-0.6, position=-1):
#     # анализ падения на одной свече, возвращает score в зависимости от степени падения и предыдущих значений
#     # print('buy_searching -> collapse_one_candle')
#
#     score = 0
#     comment = 'падение на одной свече'
#
#     drop = percent(charts[pair].data[position]['high'], charts[pair].data[position]['low'])
#
#     if (drop < threshold) and (charts[pair].data[position]['open'] > charts[pair].data[position]['close']):
#         print('---------------------------------------')
#         score += drop / threshold
#
#         average_10 = mean(charts[pair].to_list('high', 10, position, -1))
#         ave_dif_10 = percent(average_10, charts[pair].data[position]['low'])
#
#         average_3 = mean(charts[pair].to_list('high', 3, position, -1))
#         ave_dif_3 = percent(average_3, charts[pair].data[position]['low'])
#
#         min_7_1 = min(charts[pair].to_list('low', 7, position, -1))
#         change = percent(min_7_1, charts[pair].data[position]['open'])
#         if change > 0.3:
#             penalty = change / threshold
#             score += penalty
#             print('PENALTY:{} рост перед обвалом:{}%'.format(to2(penalty), to2(change)))
#
#         max_7_1 = max(charts[pair].to_list('high', 7, position, -1))
#         change = percent(max_7_1, charts[pair].data[position]['open'])
#         if change < -0.3:
#             penalty = -change / threshold * 0.75
#             score += penalty
#             print('PENALTY:{} резкое падение перед провалом:{}% '.format(to2(penalty), to2(change)))
#
#         average_20 = mean(charts[pair].to_list('high', 20, position, -1))
#         ave_dif_20 = percent(average_20, charts[pair].data[position]['low'])
#         if ave_dif_20 > threshold:
#             if ave_dif_20 < 0:
#                 penalty = -(ave_dif_20 + threshold) / threshold * 0.3
#             else:
#                 penalty = -(-ave_dif_20 + threshold) / threshold * 0.5
#             score += penalty
#             print('PENALTY:{} малая разница со средним 20:{}%'.format(to2(penalty), to2(ave_dif_20)))
#         else:
#             bonus = (ave_dif_20 + threshold) / threshold * 0.35
#             score += bonus
#             print('BONUS:{} большая разница со средним 20:{}%'.format(to2(bonus), to2(ave_dif_20)))
#
#         print('#:{}  DROP:{}%  SCORE:{}'.format(position, to2(drop), to2(score)))
#         print('разница со средним 20:', ave_dif_20, '%')
#         print('разница со средним 10:', ave_dif_10, '%')
#         print('разница со средним 3:', ave_dif_3, '%')
#         print('SCORE FINAL:', to2(score))
#
#         return {'score': score, 'comment': comment}
