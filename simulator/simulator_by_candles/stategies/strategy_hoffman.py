def hoffman(self, frame, charts, arr):
    o = charts[frame]['o']
    h = charts[frame]['h']
    l = charts[frame]['l']
    c = charts[frame]['c']
    ema_s = arr[frame]['ema_s']
    ema_f = arr[frame]['ema_f']
    ma_speed = arr[frame]['ma_speed']

    ratio = 1.5

    if not self.session:
        tail_up = (h[-2] - max(o[-2], c[-2])) / ((h[-2] - l[-2]) / 100) if (h[-2] - l[-2]) != 0 else 0
        if tail_up > 10:
            self.add_job_point('tail_up', date[-2], 1.0005 * h[-2], 6, 'red')
            if ema_f[-2] > ema_s[-2]:
                if ma_speed[-2] > 0.05:
                    open_rate = h[-2]
                    stop_loss = l[-2]
                    take_profit = open_rate + (open_rate - stop_loss) * ratio
                    self.open_session('long', open_rate, date[-1], take_profit, stop_loss)