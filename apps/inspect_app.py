import os, sys
from datetime import datetime
import json
import math

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
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_extended_data, get_gem_inspection, get_gem_markets

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
                                                    style={'display': 'inline-block', 'width': '100%', 'padding-left': 20, 'vertical-align': 'middle'}
                                                ),
                                            ],
                                            md=4,
                                            style={'padding': 0},
                                            align='center'
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dbc.Row(
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
                                                        ),
                                                    ],
                                                    id='gem_price_div',
                                                    style={'display': 'inline-block', 'width': '100%', 'padding-left': 10, 'vertical-align': 'middle'}
                                                ),
                                            ],
                                            md=4,
                                            style={'padding': 0},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [							
                                                        html.P("Select a GEM to Inspect", style={'margin-bottom': 2, 'margin-top': 0}),
                                                        dcc.Dropdown(
                                                            id='inspect_dropdown',
                                                            placeholder='Select GEM to Inspect...',
                                                            options=get_name_options(),
                                                            value=get_name_options()[0]['value'],
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
                            style={'height': 'auto', 'min-height': 60, 'padding': 5},
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



@app.callback(Output('gem_name_div', 'children'),
	[Input('inspect_dropdown', 'value'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_gem_name(gem_id, n_intervals):
    if gem_id == None:
        pass
    else:
        gem_data = get_data_recent(gem_id)
        inspect_data = get_gem_inspection(gem_id)
        market_data = get_gem_markets(gem_id)

        return [
            html.Img(src=gem_data['image'], height=50, style={'display': 'inline-block', 'padding': 5, 'vertical-align': 'top'}),
            html.H2('{}'.format(gem_data['name']), style={'display': 'inline-block', 'padding-top': 5, 'vertical-align': 'top'}),
            html.Span('({})'.format(gem_data['symbol']), 
                style={
                    'margin': 5, 
                    'font-size': 16, 
                    'color': base_colours['secondary_text'], 
                    'font-family': 'Supermolot', 
                    'display': 'inline-block', 
                    'padding': 5,
                    'vertical-align': 'bottom'
                }
            )
        ]


@app.callback(Output('gem_price_div', 'children'),
	[Input('inspect_dropdown', 'value'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_gem_price(gem_id, n_intervals):
    if gem_id == None:
        pass
    else:
        gem_data = get_extended_data(gem_id)
        inspect_data = get_gem_inspection(gem_id)
        market_data = get_gem_markets(gem_id)
        btc_now = get_data_recent('bitcoin')['current_price']
        eth_now = get_data_recent('ethereum')['current_price']

        if gem_data['price_change_percentage_24h'] > 0:
            change_color = palette['green']['50']
        elif gem_data['price_change_percentage_24h'] < 0:
            change_color = palette['red']['50']
        else:
            change_color = base_colours['secondary_text']

        return [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Span('${}'.format(round(gem_data['current_price'], 4 - int(math.floor(math.log10(abs(gem_data['current_price'])))) - 1)), 
                                style={
                                    'margin': 5, 
                                    'font-size': 26, 
                                    'color': base_colours['secondary_text'], 
                                    'font-family': 'Supermolot', 
                                    'display': 'inline-block', 
                                    'padding': 5,
                                    'vertical-align': 'middle'
                                }
                            ),
                            html.Span('({}%)'.format(round(gem_data['price_change_percentage_24h'], 1)), 
                                style={
                                    'margin': 5, 
                                    'font-size': 18, 
                                    'color': change_color,
                                    'font-family': 'Supermolot', 
                                    'display': 'inline-block', 
                                    'padding': 5,
                                    'vertical-align': 'middle'
                                }
                            ),                    
                        ],
                        width=6,
                        style={'padding': 0}, 
                        align='center'
                    ),
                    dbc.Col(
                        [
                            dbc.Row([
                                dbc.Col([
                                    html.Span(f"{gem_data['current_price']/btc_now:8f} BTC",
                                        style={
                                            'margin': 5, 
                                            'font-size': 14, 
                                            'color': base_colours['secondary_text'], 
                                            'font-family': 'Supermolot', 
                                            'display': 'inline-block', 
                                            'padding': 5,
                                            'vertical-align': 'middle'
                                        }
                                    ),
                                    html.Span('',
                                        style={
                                            'margin': 5, 
                                            'font-size': 12, 
                                            'color': base_colours['secondary_text'], 
                                            'font-family': 'Supermolot', 
                                            'display': 'inline-block', 
                                            'padding': 5,
                                            'vertical-align': 'middle'
                                        }
                                    ),
                                ], align='center'),
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Span(f"{gem_data['current_price']/eth_now:8f} ETH",
                                        style={
                                            'margin': 5, 
                                            'font-size': 14, 
                                            'color': base_colours['secondary_text'], 
                                            'font-family': 'Supermolot', 
                                            'display': 'inline-block', 
                                            'padding': 5,
                                            'vertical-align': 'middle'
                                        }
                                    ),
                                    html.Span('',
                                        style={
                                            'margin': 5, 
                                            'font-size': 12,
                                            'color': base_colours['secondary_text'],
                                            'font-family': 'Supermolot', 
                                            'display': 'inline-block', 
                                            'padding': 5,
                                            'vertical-align': 'middle'
                                        }
                                    ),
                                ], align='center'),
                            ]),
                        ],
                        width=6,
                        style={'padding': 0},
                    )
                ]
            )
        ]
