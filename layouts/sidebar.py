import os, sys
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

# path to this file location
script_dir = os.path.dirname(__file__)

from app import app, cache
from data_functions import get_data_recent
from colours import palette, base_colours

sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.A([
                html.Img(
                    src='assets/Color logo - no background.png',
                    style={'max-width': '100%', 'width': 200, 'margin': 0, 'height': 'auto'}, 
                    className='hidden-logo-md'
                )
            ], href='https://tokenfeeds.info'),
            width=12,
            style={'padding-right': '5px', 'padding-left': '5px'}
        )
    ]
)

def generate_layout():
    return html.Div(
        [
            sidebar_header,
            # we wrap the horizontal rule and short blurb in a div that can be
            # hidden on a small screen
            html.Div(
                [
                    html.Hr(),
                    #html.Hr(),
                    #html.P('User: ' + str(get_user()), id='active_user'),
                    #html.Hr(),
                ],
                id="blurb",
            ),
            # use the Collapse component to animate hiding / revealing links
            dbc.Collapse(
                [
                    dbc.Row([
                        dbc.Nav(
                            [
                                dbc.NavLink(
                                    "Overview",
                                    id='gems-page',
                                    href='/gems-overview',
                                    style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                                ),
                                dbc.NavLink(
                                    "Inspect GEM *",
                                    id='inspect-page',
                                    href='/inspect-gem',
                                    style={'padding-left': 5, 'color': base_colours['card'], 'font-size': 18}
                                ),
                                dbc.NavLink(
                                    "Trending Data", 
                                    id='trends-page',
                                    href='/trends', 
                                    style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                                ),
                                dbc.NavLink(
                                    "Macro Market *", 
                                    id='macro-page',
                                    href='/macro', 
                                    style={'padding-left': 5, 'color': base_colours['card'], 'font-size': 18}
                                ),
                                dbc.NavLink(
                                    "Wallet Tracker *", 
                                    id='wallet-page',
                                    href='/wallet', 
                                    style={'padding-left': 5, 'color': base_colours['card'], 'font-size': 18}
                                )
                            ],
                            vertical=True,
                            pills=True,
                            style={'padding-left': 15},
                        ),
                    ]),
                    dbc.Row(
                        [
                            dbc.Col([
                                html.P('* coming soon', style={'margin': 10, 'font-size': 13, 'color': base_colours['card']}),
                                html.Hr(),
                            ], xl=12),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col([
                                html.Div(
                                    [
                                        html.P('BTC: ', style={'margin': 5, 'font-size': 14, 'color': base_colours['secondary_text']}),
                                        html.Span('', style={'margin': 5, 'font-size': 14}),
                                    ],
                                    id='btc_price',
                                    style={'display': 'inline-block'}
                                ),
                                html.Div(
                                    [
                                        html.P('ETH: ', style={'margin': 5, 'font-size': 14, 'color': base_colours['secondary_text']}),
                                        html.Span('', style={'margin': 5, 'font-size': 14}),
                                    ],
                                    id='eth_price',
                                    style={'display': 'inline-block'}
                                ),
                                html.Div(
                                    [
                                        html.P('BNB: ', style={'margin': 5, 'font-size': 14, 'color': base_colours['secondary_text']}),
                                        html.Span('', style={'margin': 5, 'font-size': 14}),
                                    ],
                                    id='bnb_price',
                                    style={'display': 'inline-block', 'color': base_colours['secondary_text']}
                                ),
                                html.Hr(),
                            ], xl=12),
                        ],
                    ),
                    dbc.Row(
                        [
                            dbc.Col([
                                html.A(
                                    dbc.Button(
                                        'GEMS API',
                                        id='api-button',
                                        size='sm',
                                        className="mr-1",
                                        style={'margin': 10, 'background-color': base_colours['tf_accent2'], 'color': base_colours['black'], 'border-color': base_colours['black']},
                                        block=True,
                                    ),
                                    href='https://tokenfeeds.info/api/v1/gems/all',
                                ),
                                html.A(
                                    dbc.Button(
                                        'Portfolio Tracker',
                                        id='sheets-button',
                                        size='sm',
                                        className="mr-1",
                                        style={'margin': 10, 'background-color': base_colours['tf_accent3'], 'color': base_colours['black'], 'border-color': base_colours['black']},
                                        block=True,
                                    ),
                                    href='https://docs.google.com/spreadsheets/d/1wxgm4sU_MAJloRxBLU2_cQTaPIMbesmKhxfLoF9bEI0/edit?usp=sharing',
                                ),
                                ], xl=12),
                        ],
                        style={'padding-right': '1rem'},
                        align='end',
                    ),
                    dbc.Row(
                        [
                            dbc.Col([
                                html.Hr(),
                                html.P('version 0.0.4', style={'font-size': 11, 'font-style': 'italic', 'color': base_colours['cg_cell']}),
                            ], xl=12),
                        ],
                        style={'text-align': 'center'},
                    ),
                ],
                id='collapse',
            ),
        ],
        id="sidebar",
        #style={'background-color': '#c0c0c0'},
    )

layout = generate_layout()


@app.callback(Output('btc_price', 'children'),
    [Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_btc(n_intervals):
    price = get_data_recent('bitcoin')['current_price']
    change_24h = get_data_recent('bitcoin')['price_change_percentage_24h_in_currency']
    if change_24h > 0:
        change_color = palette['green']['50']
    elif change_24h < 0:
        change_color = palette['red']['50']

    return [
        html.P(
            [
                'BTC: ${}'.format(round(price, 2)),
                html.Span('({}%)'.format(round(change_24h, 1)), style={'margin': 5, 'font-size': 13, 'color': change_color}),
            ],
            style={'margin': 5, 'font-size': 14, 'color': base_colours['secondary_text']}
        ),
    ]


@app.callback(Output('eth_price', 'children'),
    [Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_eth(n_intervals):
    price = get_data_recent('ethereum')['current_price']
    change_24h = get_data_recent('ethereum')['price_change_percentage_24h_in_currency']
    if change_24h > 0:
        change_color = palette['green']['50']
    elif change_24h < 0:
        change_color = palette['red']['50']

    return [
        html.P(
            [
                'ETH: ${}'.format(round(price, 2)),
                html.Span('({}%)'.format(round(change_24h, 1)), style={'margin': 5, 'font-size': 13, 'color': change_color}),
            ],
            style={'margin': 5, 'font-size': 14, 'color': base_colours['secondary_text']}
        ),
    ]


@app.callback(Output('bnb_price', 'children'),
    [Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_bnb(n_intervals):
    price = get_data_recent('binancecoin')['current_price']
    change_24h = get_data_recent('binancecoin')['price_change_percentage_24h_in_currency']
    if change_24h > 0:
        change_color = palette['green']['50']
    elif change_24h < 0:
        change_color = palette['red']['50']

    return [
        html.P(
            [
                'BNB: ${}'.format(round(price, 2)),
                html.Span('({}%)'.format(round(change_24h, 1)), style={'margin': 5, 'font-size': 13, 'color': change_color}),
            ],
            style={'margin': 5, 'font-size': 14, 'color': base_colours['secondary_text']}
        ),
    ]

