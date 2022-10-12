# from datetime import datetime
# import numpy as np
import pandas as pd
import plotly
from pprint import pprint
import plotly.graph_objects as go
from inc.inc_system import *


class Graphics:
    def __init__(self, data):
        self.data = data
        self.np_open = data['charts_open']
        self.np_close = data['charts_close']
        self.np_high = data['charts_high']
        self.np_low = data['charts_low']
        self.utc_dates = data['utc_dates']
        self.timestamps = data['timestamps']

        self.points_open = data['points_open']
        self.points_close = data['points_close']
        self.amplitude = data['amplitude']
        self.do_plot_online()

    def do_plot_online(self):
        color_up = '#00B519'
        color_down = '#ff0000'
        # points_in = [{'x': self.points['open'][i]['x'], 'y': self.points['open'][i]['y']} for i in self.points['open'].keys()]
        # points_out = [{'x': self.points['close'][i]['x'], 'y': self.points['close'][i]['y']} for i in self.points['close'].keys()]

        arr = self.data
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
            opacity=.25,
            text=self.amplitude,
            increasing=dict(line=dict(color=color_up)),
            decreasing=dict(line=dict(color=color_down)),
         ))

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['bb_m_2'],
        #                  line=dict(color='yellow', width=0.8),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.7,
        #                  name='BBand middle'))
        #
        data.append(dict(x=self.utc_dates,
                         y=arr['jma_band_up'],
                         # y=arr['bb_u_2'],
                         line=dict(color='cyan', width=0.07),
                         type='scatter',
                         mode='lines',
                         showlegend=False,
                         name='BBand upper'))

        data.append(dict(x=self.utc_dates,
                         # y=arr['bb_l_2'],
                         y=arr['jma_band_down'],
                         line=dict(color='cyan', width=0.07),
                         type='scatter',
                         mode='lines',
                         showlegend=False,
                         fill='tonexty',
                         fillcolor='rgba(30, 151, 214, 0.04)',
                         name='BBand lower'))

        data.append(dict(x=self.utc_dates,
                         y=arr['ema_f'],
                         line=dict(color='crimson', width=2),
                         type='scatter',
                         mode='lines',
                         showlegend=False,
                         opacity=.8,
                         name='EMA fast'))

        data.append(dict(x=self.utc_dates,
                         y=arr['ema_m'],
                         line=dict(color='#fff', width=2),
                         type='scatter',
                         mode='lines',
                         showlegend=False,
                         opacity=.99,
                         name='EMA mid'))

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['ema_s'],
        #                  line=dict(color='cyan', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='EMA slow'))
        #
        # data.append(dict(x=self.utc_dates,
        #                  y=arr['ema_xs'],
        #                  line=dict(color='cornflowerblue', width=2),
        #                  type='scatter',
        #                  mode='lines',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  name='EMA extra slow'))

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['stoch_rsi_k'],
        #                  line=dict(color='green', width=2),
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

        # data.append(dict(x=arr['peaks']['x'],
        #                  y=arr['peaks']['y'],
        #                  mode='markers',
        #                  type='scatter',
        #                  xaxis='x1',
        #                  yaxis='y1',
        #                  name='Dataset',
        #                  marker={'size': 8, 'color': 'yellow', 'symbol': 2},
        #                  showlegend=False,
        #                  ))

        data.append(dict(x=self.points_open['x'],
                         y=self.points_open['y'],
                         mode='markers',
                         type='scatter',
                         xaxis='x1',
                         yaxis='y1',
                         name='Dataset',
                         marker={'size': 11, 'color': '#8aff00', 'symbol': self.points_open['marker']},
                         showlegend=False,
                         ))

        data.append(dict(x=self.points_close['x'],
                         y=self.points_close['y'],
                         mode='markers',
                         type='scatter',
                         xaxis='x1',
                         yaxis='y1',
                         name='Dataset',
                         marker={'size': 11, 'color': 'red', 'symbol': self.points_close['marker']},
                         showlegend=False,
                         ))

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

        # data.append(dict(x=self.utc_dates,
        #                  y=arr['ema_dif'],
        #                  # line=dict(color='red', width=1.1),
        #                  type='bar',
        #                  marker_line_width=0,
        #                  yaxis='y3',
        #                  showlegend=False,
        #                  opacity=.99,
        #                  opacity=.99,
        #                  name='EMA DIF'))

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
        layout['title'] = {'text': self.data['pair'] + ' ' + self.data['frame'], 'y': 0.95, 'x': 0.09, 'font': {'size': 14, 'color': '#ccc'}}
        layout['hovermode'] = 'x unified'
        layout['hoverlabel'] = {'font': {'color': '#ccc'}}
        layout['paper_bgcolor'] = '#1e1e1e'
        layout['plot_bgcolor'] = '#1e1e1e'
        layout['xaxis'] = dict(
            domain=[0, 1],
            rangeslider={'visible': False},
            gridcolor='#2f2f2f',
            tickfont={'size': 11, 'color': '#ccc'},
            autorange=True,
            showgrid=True,
            zeroline=False,
            showline=False,
            showticklabels=True,
            tickformat='%H:%M\n%d %b',
        )

        layout['yaxis'] = dict(domain=[0.35, 1], autorange=True, fixedrange=False, gridcolor='#2f2f2f', tickfont={'size': 11, 'color': '#cccccc'})
        layout['yaxis2'] = dict(domain=[0, 0.13], autorange=True, fixedrange=False, gridcolor='#2f2f2f', zeroline=False, showline=False, tickfont={'size': 11, 'color': '#cccccc'})
        layout['yaxis3'] = dict(domain=[0.16, 0.28], gridcolor='#2f2f2f', zeroline=False, showline=False, tickfont={'size': 11, 'color': '#cccccc'}, tickvals=[30, 70])
        layout['yaxis4'] = dict(domain=[0.16, 0.23], gridcolor='#2f2f2f', zeroline=False, showline=False, tickfont={'size': 11, 'color': '#cccccc'}, tickvals=[30, 70], overlaying='y3')
        layout['yaxis5'] = dict(domain=[0.16, 0.23], gridcolor='#2f2f2f', zeroline=False, showline=False, tickfont={'size': 11, 'color': '#cccccc'}, overlaying='y3')

        layout['legend'] = dict(orientation='h', y=0.99, x=0.01, yanchor='top', font={'color': '#ccc'})
        layout['dragmode'] = 'pan'

        fig = go.Figure(data=data, layout=layout)
        config = dict({'scrollZoom': True})
        fig.show(config=config)
