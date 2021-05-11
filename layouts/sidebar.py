import os, sys
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from colours import sidebar_grey

# path to this file location
script_dir = os.path.dirname(__file__)
from colours import base_colours

sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.Img(
                src='assets/Color logo - no background.png',
                style={'max-width': '100%', 'width': 200, 'margin': 0, 'height': 'auto'}, 
                className='hidden-logo-md'
            ),
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
                dbc.Nav(
                    [
                        dbc.NavLink(
                            "GEMS Overview",
                            id='gems-page',
                            href='/gems-overview',
                            style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Token Overview",
                            id='token-page',
                            href='/token-overview',
                            style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Trending Data", 
                            id='trends-page',
                            href='/trends', 
                            style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Macro Market", 
                            id='macro-page',
                            href='/macro', 
                            style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Wallet Tracker", 
                            id='wallet-page',
                            href='/wallet', 
                            style={'padding-left': 5, 'color': '#ffffff', 'font-size': 18}
                        )
                    ],
                    vertical=True,
                    pills=True,
                ),
                id="collapse",
            ),
            dbc.Row([dbc.Col([html.Hr()])]),
            dbc.Row(
                [
                    dbc.Col([
                        html.A(
                            dbc.Button(
                                'GEMS API',
                                id='api-button',
                                size='sm',
                                className="mr-1",
                                style={'margin': 10, 'background-color': base_colours['tf_accent2'], 'color': base_colours['black']},
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
                                style={'margin': 10, 'background-color': base_colours['tf_accent3'], 'color': base_colours['black']},
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
                        html.P('version 0.0.2', style={'font-size': 11, 'font-style': 'italic', 'color': base_colours['cg_cell']}),
                    ], xl=12),
                ],
                style={'text-align': 'center'},
            ),
        ],
        id="sidebar",
        #style={'background-color': '#c0c0c0'},
    )

layout = generate_layout()
