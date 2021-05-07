import os, sys
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc

from colours import sidebar_grey

# path to this file location
script_dir = os.path.dirname(__file__)


sidebar_header = dbc.Row(
    [
        dbc.Col(html.H1("TokenFeeds", className="display-6", style={'fontSize': '22pt'})),
        dbc.Col(
            html.Button(
                # use the Bootstrap navbar-toggler classes to style the toggle
                html.Span(className="navbar-toggler-icon"),
                className="navbar-toggler",
                # the navbar-toggler classes don't set color, so we do it here
                style={
                    "color": "rgba(0,0,0,.5)",
                    "border-color": "rgba(0,0,0,.1)",
                },
                id="toggle",
            ),
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        ),
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
                            style={'padding-left': 5, 'color': '#000000', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Token Overview",
                            id='token-page',
                            href='/token-overview',
                            style={'padding-left': 5, 'color': '#000000', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Trending Data", 
                            id='trends-page',
                            href='/trends', 
                            style={'padding-left': 5, 'color': '#000000', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Macro Market", 
                            id='macro-page',
                            href='/macro', 
                            style={'padding-left': 5, 'color': '#000000', 'font-size': 18}
                        ),
                        dbc.NavLink(
                            "Wallet Tracker", 
                            id='wallet-page',
                            href='/wallet', 
                            style={'padding-left': 5, 'color': '#000000', 'font-size': 18}
                        )
                    ],
                    vertical=True,
                    pills=True,
                ),
                id="collapse",
            ),
        ],
        id="sidebar",
        style={'background-color': '#c0c0c0'},
    )

layout = generate_layout()
