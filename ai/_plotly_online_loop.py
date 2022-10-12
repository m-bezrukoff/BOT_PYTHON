# from datetime import datetime
# import numpy as np
import pandas as pd
import plotly
import plotly.graph_objects as go
from time import sleep
from random import randint


def do_plot_online():

    x = [i for i in range(10)]
    y = [randint(1, 10) for i in range(10)]


    data = [(dict(x=x,
                     y=y,
                     type='scatter',
                     mode='lines',
                     yaxis='y2',
                     showlegend=False,
                     opacity=.8,
                     name='SIGNAL'))]


    layout = {}
    layout['paper_bgcolor'] = '#1e1e1e'
    layout['plot_bgcolor'] = '#212121'
    layout['xaxis1'] = dict(
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

    fig = go.Figure(data=data, layout=layout)
    config = dict({'scrollZoom': True})
    fig.show(config=config)


# while True:
do_plot_online()
# sleep(10)
