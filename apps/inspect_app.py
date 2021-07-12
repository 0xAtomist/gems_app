import os, sys
from datetime import datetime
import json

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

import pandas as pd
from collections import OrderedDict

from app import app, cache
from colours import *
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_extended_data, get_filtered_df

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


def get_name_options():
    name_options = []
    gem_list = get_gem_list(master)
    ticker_list = []
    name_list = []
    for gem in gem_list:
        ticker_list.append(master['gems'][gem]['symbol'])
        name = get_data_recent(gem)['name']
        name_list.append(name)
    df = pd.DataFrame(data={'ticker': ticker_list, 'gem': gem_list, 'name': name_list})
    df = df.sort_values(by='name', key=lambda col: col.str.lower())
    for i in df.index:
        name_options.append({'label': '{} ({})'.format(df.loc[i]['name'], df.loc[i]['ticker']), 'value': df.loc[i]['gem']})
    return name_options


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.Img(),
                                                        html.H2(''),
                                                        html.Span('', style={'margin': 5, 'font-size': 16}),
                                                    ],
                                                    id='gem_name_div',
                                                ),
                                            ],
                                            md=4,
                                            style={'padding': 0},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dbc.Col(
                                                            [
                                                                html.Span('', style={'margin': 5, 'font-size': 18}),
                                                                html.Span('', style={'margin': 5, 'font-size': 18}),
                                                            ],
                                                            xl=6,
                                                            style={'padding': 0}
                                                        ),
                                                        dbc.Col(
                                                            [
                                                                dbc.Row([
                                                                    html.Span('', style={'margin': 5, 'font-size': 16}),
                                                                    html.Span('', style={'margin': 5, 'font-size': 16}),
                                                                ]),
                                                                dbc.Row([
                                                                    html.Span('', style={'margin': 5, 'font-size': 16}),
                                                                    html.Span('', style={'margin': 5, 'font-size': 16}),
                                                                ]),
                                                            ],
                                                            xl=6,
                                                            style={'padding': 0},
                                                        )
                                                    ],
                                                    id='gem_price_div',
                                                ),
                                            ],
                                            md=4,
                                            style={'padding': 0},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dcc.Dropdown(
                                                            id='inspect_dropdown',
                                                            placeholder='Select GEM to Inspect...',
                                                            options=get_name_options(),
                                                            multi=False,
                                                            style={'width': 'calc(100%-40px)', 'padding-right': 5},
                                                        ),
                                                    ],
                                                    id='gem_dropdown_div',
                                                ),
                                            ],
                                            md=4,
                                            align='center',
                                        ),
                                    ],
                                    style={'padding': 0},
                                ),
                            ],
                            id='inspect_ribbon',
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 60, 'padding': 10},
                        ),
                    ],
                    xl=12,
                    style={'padding': 0},
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 380},
                        ),
                    ],
                    xl=8,
                    style={'padding': 0}
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 380},
                        ),
                    ],
                    xl=4,
                    style={'padding': 0}
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 250},
                        ),
                    ],
                    xl=4,
                    style={'padding': 0}
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 250},
                        ),
                    ],
                    xl=8,
                    style={'padding': 0}
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 200},
                        ),
                    ],
                    xl=12,
                    style={'padding': 0}
                ),
            ],
        ),
    ],
    id='inspect-gem-container',
)



