# from datetime import datetime
# import numpy as np
import pandas as pd
import plotly
from pprint import pprint
import plotly.graph_objects as go
from inc.inc_system import *


class Graphics:
    def __init__(self, _job):
        self.data = _job.data
        self.tools = _job.indicators.tools
        self.pair = self.data.pair
        self.frame = _job.data.frame
        self.margin = self.data.margin_candles
        self.from_timestamp = self.data.from_timestamp
        self.job_points = _job.job.job_points
        self.job_lines = _job.job.job_lines
        self.grid_level_lines = _job.job.grid_level_lines

        self.np_open = self.data.charts[self.frame]['o'][self.margin:]
        self.np_close = self.data.charts[self.frame]['c'][self.margin:]
        self.np_high = self.data.charts[self.frame]['h'][self.margin:]
        self.np_low = self.data.charts[self.frame]['l'][self.margin:]
        self.utc_dates = self.data.charts[self.frame]['utc_date'][self.margin:]
        self.timestamps = self.data.charts[self.frame]['timestamp'][self.margin:]
        self.amplitude = self.data.charts[self.frame]['amplitude'][self.margin:]

        self.arr = {}
        for attr in _job.indicators.arr[self.frame]:
            if 'point' in attr:
                self.arr[attr] = _job.indicators.arr[self.frame][attr]   # точки не обрезаем
            else:
                self.arr[attr] = _job.indicators.arr[self.frame][attr][self.margin:]     # обрезаем только индикаторы
        self.do_plot_online()

    def do_plot_online(self):
        color_up = '#00B519'
        color_down = '#ff0000'
        arr = self.arr
        data = list()

        data.append(dict(
            type='candlestick',
            open=self.np_open,
            high=self.np_high,
            low=self.np_low,
            close=self.np_close,
            x=self.utc_dates,
            showlegend=False,
            name='',
            opacity=.3,
            text=self.amplitude,
            increasing=dict(line=dict(color=color_up)),
            decreasing=dict(line=dict(color=color_down)),
         ))

        for name, config in self.tools.items():
            match config['method']:
                case 'EMA' | 'JMA' | 'TEMA':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name],
                        type='scatter',
                        mode='lines',
                        line=dict(color=config['color'], width=config['width']),
                        showlegend=False,
                        opacity=.99,
                        name=f'{config["method"]} {config["period"]}'))

                case 'MA_SPEED':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name],
                        type='scatter',
                        mode='lines',
                        line=dict(color=config['color'], width=config['width']),
                        yaxis='y2',
                        showlegend=False,
                        opacity=.99,
                        name=f'{config["method"]} SPEED'))

                case 'MA_CHANNEL':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name + '_u'],
                        type='scatter',
                        mode='lines',
                        line=dict(color='rgba(30, 151, 214, 0.5)', width=1),
                        showlegend=False,
                        name=f'{config["method"]} UPPER'))

                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name + '_l'],
                        type='scatter',
                        mode='lines',
                        line=dict(color='rgba(30, 151, 214, 0.5)', width=1),
                        showlegend=False,
                        fill='tonexty',
                        fillcolor='rgba(30, 151, 214, 0.1)',
                        name=f'{config["method"]} LOWER'))

                case 'BB_B':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name + '_u'],
                        type='scatter',
                        mode='lines',
                        line=dict(color='rgba(30, 151, 214, 0.5)', width=1),
                        showlegend=False,
                        name=f'{config["method"]} UPPER BAND'))

                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name + '_l'],
                        type='scatter',
                        mode='lines',
                        line=dict(color='rgba(30, 151, 214, 0.5)', width=0.7),
                        showlegend=False,
                        fill='tonexty',
                        fillcolor='rgba(30, 151, 214, 0.1)',
                        name=f'{config["method"]} LOWER BAND'))

                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name + '_m'],
                        type='scatter',
                        mode='lines',
                        line=dict(color='rgba(30, 151, 214, 1)', width=1),
                        showlegend=False,
                        name=f'{config["method"]} MA'))

                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name + '_b'],
                        type='scatter',
                        mode='lines',
                        line=dict(color='rgba(30, 151, 214, 1)', width=1),
                        yaxis='y3',
                        showlegend=False,
                        opacity=.99,
                        name=f'{config["method"]} %B'))

                    data.append(dict(
                        x=[self.utc_dates[0], self.utc_dates[-1]],
                        y=[1, 1],
                        type='scatter',
                        mode='lines',
                        line=dict(color='#2f2f2f', width=1),
                        yaxis='y3',
                        name=f'{config["method"]} SPEED'))

                case 'MA_CANDLE_RELATION':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name],
                        type='scatter',
                        mode='lines',
                        line=dict(color=config['color'], width=config['width']),
                        yaxis='y3',
                        showlegend=False,
                        opacity=.99,
                        name=f'{config["method"]} SPEED'))

                case 'AO':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name],
                        # marker=dict(color=arr['jma_colors']),
                        type='bar',
                        yaxis='y2',
                        marker_line_width=0,
                        showlegend=False,
                        opacity=.5,
                        name=f'{config["method"]}'))

                case 'ADX':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name],
                        # marker=dict(color=arr['jma_colors']),
                        type='bar',
                        yaxis='y4',
                        marker_line_width=0,
                        showlegend=False,
                        opacity=.5,
                        name=f'{config["method"]}'))

                case 'ATR':
                    data.append(dict(
                        x=self.utc_dates,
                        y=arr[name],
                        type='scatter',
                        mode='lines',
                        line=dict(color='white', width=0.5),
                        yaxis='y2',
                        marker_line_width=0,
                        showlegend=False,
                        name=f'{config["method"]}'))

        for name, config in self.job_points.items():
            data.append(dict(x=config['x'],
                             y=config['y'],
                             mode='markers',
                             type='scatter',
                             xaxis='x1',
                             yaxis='y1',
                             name=name,
                             marker=dict(size=config['size'], color=config['color'], symbol=config['symbol']),
                             showlegend=False,
                             ))

        for config in self.job_lines:
            data.append(dict(x=[config['x1'], config['x2']],
                             y=[config['y1'], config['y2']],
                             mode='lines',
                             type='scatter',
                             xaxis='x1',
                             yaxis='y1',
                             name=f'{to2(config["result"])}%',
                             line=dict(color=config['color'], width=config['size']),
                             showlegend=False,
                             ))

        for config in self.grid_level_lines:
            data.append(dict(x=[self.utc_dates[0], self.utc_dates[-1]],
                             y=[config['y'], config['y']],
                             mode='lines',
                             type='scatter',
                             xaxis='x1',
                             yaxis='y1',
                             line=dict(color=config['color'], width=config['size']),
                             showlegend=False,
                             ))

        # data.append(dict(
        #     type='candlestick',
        #     open=self.data.charts[self.frame]['ha_o'][self.margin:],
        #     high=self.data.charts[self.frame]['ha_h'][self.margin:],
        #     low=self.data.charts[self.frame]['ha_l'][self.margin:],
        #     close=self.data.charts[self.frame]['ha_c'][self.margin:],
        #     x=self.utc_dates,
        #     showlegend=False,
        #     name='',
        #     opacity=.5,
        #     text=self.amplitude,
        #     increasing=dict(line=dict(color=color_up)),
        #     decreasing=dict(line=dict(color=color_down)),
        #  ))

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['bb_m_2'],
        #                  line=dict(color='yellow', width=0.8),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.7,
        #                  name='BBand middle'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  # y=arr['jma_band_up'],
        #                  y=arr['bb_m_2'],
        #                  line=dict(color='cyan', width=0.2),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  name='BBand medium'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=self.data.charts[self.frame]['delta'][self.margin:],
        #                  # marker=dict(color=arr['bb_dif_colors']),
        #                  marker_line_width=0,
        #                  type='bar',
        #                  yaxis='y4',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='bb_dif'))
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['stoch_f'],
        #                  line=dict(color='green', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y4',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='stoch_f'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['stoch_s'],
        #                  line=dict(color='#fff', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y4',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='stoch_s'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['stoch_rsi_k'],
        #                  line=dict(color='red', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y4',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='stoch_rsi_k'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['stoch_rsi_d'],
        #                  line=dict(color='purple', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y4',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='stoch_rsi_d'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['jma_macd'],
        #                  marker=dict(color=arr['jma_colors']),
        #                  type='bar',
        #                  yaxis='y2',
        #                  marker_line_width=0,
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='JMA MACD'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['jma_signal'],
        #                  line=dict(color='yellow', width=1.1),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y2',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='JMA MACD SIGNAL'))

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['atr'],
        #                  line=dict(color='red', width=1.1),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y2',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='ATR'))

        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['ema_diff'],
        #                  type='bar',
        #                  yaxis='y2',
        #                  marker_line_width=0,
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='EMA diff'))

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['macd'],
        #                  line=dict(color='cyan', width=1.1),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y2',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='MACD'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['macd_s'],
        #                  line=dict(color='yellow', width=1.1),
        #                  type='scatter',
        #                  mode='lines',
        #                  yaxis='y2',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='MACD SIGNAL'))

        # colors = [color_down if i == 0 else color_up if arr['close'][i] > arr['close'][i - 1] else color_down for i in range(len(arr['close']))]
        # data.append(dict(x=arr['date'],
        #                  y=arr['vol'],
        #                  marker=dict(color=colors),
        #                  type='bar',
        #                  yaxis='y3',
        #                  marker_line_width=0,
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='Volume'))

        # data.append(dict(x=arr['ichimoku']['date'],
        #                  y=arr['ichimoku']['conversion'],
        #                  line=dict(color='cyan', width=1),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='conversion'))
        #
        # data.append(dict(x=arr['ichimoku']['date'],
        #                  y=arr['ichimoku']['base'],
        #                  line=dict(color='orange', width=1),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='base'))
        #
        # data.append(dict(x=arr['ichimoku']['date'],
        #                  y=arr['ichimoku']['senkou_span_a'],
        #                  line=dict(color='green', width=0.5),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='senkou_span_a'))
        #
        # data.append(dict(x=arr['ichimoku']['date'],
        #                  y=arr['ichimoku']['senkou_span_b'],
        #                  line=dict(color='red', width=0.5),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.5,
        #                  fill='tonexty',
        #                  fillcolor='rgba(30, 151, 214, 0.2)',
        #                  name='senkou_span_b'))
        #
        # data.append(dict(x=arr['ichimoku']['date'],
        #                  y=arr['ichimoku']['lagging'],
        #                  line=dict(color='darkviolet', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.5,
        #                  name='lagging'))

        layout = dict()
        title = f'{self.data.params["pair"]}   {self.frame}   {self.data.params["from"]} - {self.data.params["to"]}'
        layout['title'] = dict(text=title, y=0.97, x=0.06, font=dict(size=12, color='#ccc'))
        layout['hovermode'] = 'x unified'
        layout['hoverlabel'] = dict(font=dict(color='#ccc'))
        layout['paper_bgcolor'] = '#1e1e1e'
        layout['plot_bgcolor'] = '#1e1e1e'

        layout['xaxis'] = dict(
            domain=[0, 1],
            rangeslider=dict(visible=False),
            gridcolor='#2f2f2f',
            tickfont=dict(size=11, color='#ccc'),
            autorange=True,
            showgrid=True,
            zeroline=False,
            showline=False,
            showticklabels=True,
            tickformat='%H:%M\n%d %b',
        )

        layout['yaxis'] = dict(
            domain=[0.35, 1],
            autorange=True,
            fixedrange=False,
            gridcolor='#2f2f2f',
            tickfont=dict(size=11, color='#cccccc'))

        layout['yaxis2'] = dict(
            domain=[0, 0.13],
            autorange=True,
            fixedrange=False,
            gridcolor='#2f2f2f',
            zeroline=False,
            showline=False,
            tickfont=dict(size=11, color='#cccccc'))

        layout['yaxis3'] = dict(
            domain=[0.16, 0.28],
            gridcolor='#2f2f2f',
            zeroline=True,
            zerolinecolor='#2f2f2f',
            showline=False,
            tickfont=dict(size=11, color='#cccccc'),
            tickvals=[30, 70])

        layout['yaxis4'] = dict(
            domain=[0.16, 0.23],
            gridcolor='#2f2f2f',
            zeroline=True,
            zerolinecolor='#2f2f2f',
            showline=False,
            tickfont=dict(size=11, color='#cccccc'),
            tickvals=[30, 70],
            overlaying='y3')

        layout['yaxis5'] = dict(
            domain=[0.16, 0.23],
            gridcolor='#2f2f2f',
            zeroline=False,
            showline=False,
            tickfont=dict(size=11, color='#cccccc'))

        layout['legend'] = dict(orientation='h', y=0.99, x=0.01, yanchor='top', font=dict(color='#ccc'))
        layout['dragmode'] = 'pan'

        fig = go.Figure(data=data, layout=layout)
        config = dict({'scrollZoom': True})
        fig.show(config=config)
