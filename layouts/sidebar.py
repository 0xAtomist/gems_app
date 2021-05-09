import os, sys
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from colours import sidebar_grey

# path to this file location
script_dir = os.path.dirname(__file__)


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
        ],
        id="sidebar",
        #style={'background-color': '#c0c0c0'},
    )

layout = generate_layout()
