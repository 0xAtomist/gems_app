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


layout = html.Div(
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
                                html.Span('', style={'margin': 5, 'font-size': 18}),
                                html.Span('', style={'margin': 5, 'font-size': 16}),
                                dcc.Dropdown(
                                    id='inspect_dropdown',
                                    options=get_gem_options(),
                                    multi=False,
                                    value=[],
                                    #style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                ),
                            ],
                            id='inspect_ribbon',
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 60, 'display': 'inline-block'},
                        ),
                    ],
                    xl=12,
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
                            style={'height': 'auto', 'min-height': 320},
                        ),
                    ],
                    xl=9,
                    style={'padding': 0}
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 320},
                        ),
                    ],
                    xl=3,
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
                            style={'height': 'auto', 'min-height': 320},
                        ),
                    ],
                    xl=3,
                    style={'padding': 0}
                ),
                dbc.Col(
                    [
                        html.Div(
                            [
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 320},
                        ),
                    ],
                    xl=9,
                    style={'padding': 0}
                ),
            ],
        ),
    ],
    id='inspect-gem-container',
)



