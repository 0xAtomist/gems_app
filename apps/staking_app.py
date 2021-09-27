import os, sys
from datetime import datetime, timedelta, date
import json
import requests
import time

from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol, Group
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots

import pandas as pd
from collections import OrderedDict

from app import app, cache
from colours import *
from data_functions import get_gem_info, get_uni_data, get_staked_data


master = get_gem_info()


graph_config = {
    'modeBarButtonsToRemove': [
        'pan2d', 'lasso2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
        'hoverClosestCartesian','hoverCompareCartesian', 'toggleSpikelines', 'zoom2d',
        'sendDataToCloud', 'hoverClosestPie', 'toggleHover', 'resetViewMapbox'
    ],
    'displaylogo': False,
    'displayModeBar': False,
}

# Set line styles for the list of GEMS
gem_style = []
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, None])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dash'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dot'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dashdot'])


GMX_contract = "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a"
sGMX_contract = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"
GMX_ETH_LP = '0x80a9ae39310abf666a87c743d6ebbd0e8c42158e'

API_key = "YWR5E9YUBPE2X6KNXG99D2MX1UHPYDFDBGT"


def generate_staked_trend(df, dff, y_var, y_text, hover_temp):
    fig_range = make_subplots(specs=[[{"secondary_y": True}]])
    fig_range.add_trace(
        go.Scatter(
            x=df.index, 
            y=df['usd_price'], 
            name='GMX/USD Price', 
            hovertemplate='%{y:,.5f}',
            line=dict(color=base_colours['tf_accent3']),
            textfont=dict(family='Supermolot', color=base_colours['text'], size=13),
        ),
        secondary_y=False
    )
    fig_range.add_trace(
        go.Scatter(
            x=dff['timestamp'], 
            y=dff[y_var], 
            name='Total Staked', 
            hovertemplate=hover_temp,
            line=dict(color=base_colours['tf_accent']),
            textfont=dict(family='Supermolot', color=base_colours['text'], size=13),
            customdata=round(dff[y_var]/6490429*100, 2)
        ),
        secondary_y=True
    )
    fig_range.update_layout(
        plot_bgcolor='#434343',
        paper_bgcolor=base_colours['card'],
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor=base_colours['secondary_text'],
            title=dict(text='GMX/ETH'),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            ticksuffix='   ',
            tickprefix='',
#            dtick=round(max(df['price']), 3)/5
            #range=[min(df['price']), max(df['price'])]

        ),
        yaxis2=dict(
            #gridcolor=base_colours['secondary_text'],
            showgrid=False,
            title=dict(text=y_text),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            ticksuffix='   ',
            tickprefix='',
#            dtick=round(max(dff[y_var])-min(dff[y_var]), -5)/5
#            scaleanchor='y1',
            #range=[min(dff[y_var]), max(dff[y_var])]
        ),
        showlegend=True,
        font={'color': base_colours['primary_text']},
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['black'])),
        hovermode='x',
        height=550,
        legend=dict(
            font=dict(family='Supermolot', color=base_colours['text']),
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    fig_range.update_xaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1) #, rangeslider_visible=True)

    return fig_range




layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.P('Historical View of GMX Price and Total Staked Supply', id='sGMX_trend_tip', style={'text-align': 'center'}),
                                dcc.Graph(
                                    id='trend_sGMX',
                                    config=graph_config,
                                    figure=generate_staked_trend(get_uni_data('gmx', 365), get_staked_data('gmx') ,'cum_value', 'Staked GMX Count', '%{y:,.0f} (%{customdata}%)')
                                )
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 600},
                        ),
                    ],
                    xl=12,
                    style={'padding': 0}
                ),
            ],
        ),
    ],
    id='staking-container',
)


@app.callback(Output('trend_sGMX', 'figure'),
	[Input('chart-interval', 'n_intervals')])
def update_trend_price(n_intervals):
    return generate_staked_trend(get_uni_data('gmx', 365), get_staked_data('gmx'), 'cum_value', 'Staked GMX Count', '%{y:,.0f} <b>(%{customdata}%)</b>')


