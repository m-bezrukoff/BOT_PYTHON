# from datetime import datetime
# import numpy as np
import pandas as pd
from plotly.offline import plot


def do_plot(points, charts, arr_open, arr_close, arr_high, arr_low, arr_volume, xdate, ema, signal, macd, macd_colors):

    # df = pd.DataFrame(charts)

    color_up = '#00B519'
    color_down = '#ff0000'

    data = []
    layout = dict()
    fig = dict(data=data, layout=layout)

    fig['layout'] = dict()
    fig['layout']['paper_bgcolor'] = '#1e1e1e'
    fig['layout']['plot_bgcolor'] = '#212121'

    fig['layout']['xaxis1'] = dict(
        domain=[0, 1],
        rangeslider={'visible': False},
        gridcolor='#2f2f2f',
        tickfont={'size': 11, 'color': '#cccccc'},
        autorange=True,
        showgrid=True,
        zeroline=False,
        showline=False,
        showticklabels=True,
        tickformat='%H:%M:%S',
        dtick=100
        # gridwidth=10
    )

    fig['layout']['yaxis1'] = dict(domain=[0.25, 1], autorange=True, fixedrange=False, gridcolor='#2f2f2f', tickfont={'size': 11, 'color': '#cccccc'})
    fig['layout']['yaxis3'] = dict(domain=[0.16, 0.23], gridcolor='#2f2f2f', zeroline=False, showline=False, tickfont={'size': 11, 'color': '#cccccc'})
    fig['layout']['yaxis2'] = dict(domain=[0, 0.15], gridcolor='#2f2f2f', zeroline=False, showline=False, tickfont={'size': 11, 'color': '#cccccc'})

    fig['layout']['legend'] = dict(orientation='h', y=0.99, x=0.01, yanchor='top', font={'color': '#ccc'})
    fig['layout']['dragmode'] = 'pan'

    fig['data'].append(dict(type='candlestick',
                            opacity=.3,
                            open=arr_open,
                            high=arr_high,
                            low=arr_low,
                            close=arr_close,
                            x=xdate,
                            xaxis='x1',
                            yaxis='y1',
                            increasing=dict(line=dict(color=color_up)),
                            decreasing=dict(line=dict(color=color_down)),
                            showlegend=False))

    # fig['data'].append(dict(x=points['minimums']['date'],
    #                         y=points['minimums']['val'],
    #                         mode='markers',
    #                         type='scatter',
    #                         xaxis='x1',
    #                         yaxis='y1',
    #                         name='Dataset',
    #                         marker={'size': 12, 'color': '#ffffff'},
    #                         showlegend=False,
    #                         ))
    # fig['data'].append(dict(x=points['predictions']['date'],
    #                         y=points['predictions']['val'],
    #                         mode='markers',
    #                         type='scatter',
    #                         xaxis='x1',
    #                         yaxis='y1',
    #                         name='Predicted',
    #                         marker={'size': 6, 'color': '#ff9600'},
    #                         showlegend=False,
    #                         ))
    fig['data'].append(dict(x=xdate,
                            y=macd,
                            marker=dict(color=macd_colors),
                            type='bar',
                            yaxis='y2',
                            marker_line_width=0,
                            showlegend=False,
                            opacity=.5,
                            name='MACD'))
    fig['data'].append(dict(x=xdate,
                            y=ema,
                            line=dict(color='#ff9600', width=.7),
                            type='scatter',
                            mode='lines',
                            yaxis='y2',
                            showlegend=False,
                            opacity=.8,
                            name='EMA'))
    fig['data'].append(dict(x=xdate,
                            y=signal,
                            line=dict(color='#fff', width=.7),
                            type='scatter',
                            mode='lines',
                            yaxis='y2',
                            showlegend=False,
                            opacity=.8,
                            name='SIGNAL'))

    colors = [color_down if i == 0 else color_up if arr_close[i] > arr_close[i-1] else color_down for i in range(len(arr_close))]

    fig['data'].append(dict(x=xdate,
                            y=arr_volume,
                            marker=dict(color=colors),
                            type='bar',
                            yaxis='y3',
                            marker_line_width=0,
                            showlegend=False,
                            opacity=.5,
                            name='Volume'))

    plot(fig, config={'scrollZoom': True})
