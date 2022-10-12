from inc.inc_functions import percent, add_percent
from inc.inc_system import to2


def profit_calculator(charts, params, points_in, points_out, no_print=False):
    profit_deals = 0
    lose_deals = 0
    global_profit = 0
    out_unix_time = 0
    start_time = charts[0]['timestamp']

    try:
        if points_in[-1]['timestamp'] > points_out[-1]['timestamp']:
            #   deleting last unclosed enter point
            _ = 0
            for _ in range(-1, -len(points_in['x']), -1):
                if points_in['timestamp'][_] < points_out['timestamp'][-1]:
                    break
            points_in['timestamp'] = points_in['timestamp'][:_+1]
            points_in['x'] = points_in['x'][:_+1]
            points_in['y'] = points_in['y'][:_+1]
    except IndexError:
        pass

    for i in range(len(points_in['x'])):
        loss_text = ''

        in_value = points_in['y'][i]
        in_time = points_in['x'][i]
        in_unix_time = int(points_in['timestamp'][i])

        out_value = 0
        out_time = 0

        if in_unix_time > out_unix_time:
            for y in range(len(points_out['x'])):

                out_value = points_out['y'][y]
                out_time = points_out['x'][y]
                out_unix_time = int(points_out['timestamp'][y])

                if out_unix_time > in_unix_time:
                    # print('->', out_time, out_value)
                    break

            profit = percent(in_value, out_value) - 0.25
            in_position = int((in_unix_time - start_time) / params['c_size'])
            out_position = int((out_unix_time - start_time) / params['c_size'])

            for z in charts[in_position:out_position]:
                if percent(in_value, z['low']) < params['stop_loss']:
                    out_value = add_percent(in_value, params['stop_loss'] - 0.2)
                    out_time = z['utc_date']
                    out_unix_time = z['timestamp']
                    loss_text = '-> stop_loss {} at {}'.format(z['utc_date'], out_value)
                    profit = percent(in_value, out_value) - 0.25
                    break

            if profit > 0:
                profit_deals += 1
            else:
                lose_deals += 1

            global_profit += profit

            if not no_print:
                if profit < 0:
                    print('\033[31m{} {} {}% {}\033[0m'.format(in_time, out_time, to2(profit), loss_text))
                elif profit > 1:
                    print('\033[32m{} {} {}%\033[0m'.format(in_time, out_time, to2(profit)))
                else:
                    print('{} {} {}% {}'.format(in_time, out_time, to2(profit), loss_text))
                # if loss_text:
                #     print(loss_text)

    profit = round(global_profit, 3)

    try:
        success = round(profit_deals * 100 / (profit_deals + lose_deals), 2)
    except ZeroDivisionError:
        success = 0

    if not no_print:
        print('-' * 40)
        if profit < 0:
            print('profit \033[31m{}%\033[0m  success: \033[31m{}%\033[0m ({} / {})'.format(profit, success, profit_deals, lose_deals))
        else:
            print('profit \033[32m{}%\033[0m  success: \033[32m{}%\033[0m ({} / {})'.format(profit, success, profit_deals, lose_deals))
    return [profit, success, profit_deals, lose_deals]
