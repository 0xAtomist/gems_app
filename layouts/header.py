import os, sys
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from datetime import timedelta
from dash.dependencies import Input, Output, State
from collections import OrderedDict

from app import app
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_slider
from colours import base_colours

# Get location info
master = get_gem_info()


def get_time_today():
	return int(pd.Timestamp.today().timestamp() + timedelta(days=1).total_seconds())


def generate_layout():
	return html.Div(
		[
			dcc.Interval(id='live-interval', interval=1*60*1000, n_intervals=0),
			dcc.Interval(id='chart-interval', interval=10*1000, n_intervals=0),
			dcc.Store(id='filter-store', storage_type='memory'),
			dcc.Store(id='filter-trend', storage_type='memory'),
			dcc.Store(id='gmx_shapes', storage_type='local'),
			dbc.Row(
				[
					dbc.Col(
						html.Img(
							src='/assets/gem-stone.png',
							style={
								'height': 'auto',
								'max-width': '100%',
								'width': 70,
								'margin-left': 25,
							},
							className='hidden-logo-sm',
							id='logo-head',
						),
						sm=2,
						style={'padding': 0},
					),
					dbc.Col(
						[
							html.H3(
								'GEMS Alliance',
								style={'margin-bottom': 0, 'text-align': 'center'},
							),
							html.H5(
								'Performance Overview',
								style={'margin-top': 5, 'text-align': 'center'},
								id='page-title',
							)
						],
						sm=4,
						style={'padding': 0},
					),
					dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dbc.DropdownMenu(
                                                            id='everything-gems',
                                                            nav=True,
                                                            label='GEMS Directory',
                                                            bs_size='lg',
                                                            right=True,
                                                            className='mb-3',
                                                            toggle_style={'border-radius': '4px', 'font-size': 18, 'text-align': 'right', 'max-width': 170},
                                                            children=[
                                                                dbc.DropdownMenuItem('GEMS Docs (Coda)', header=True),
                                                                dbc.DropdownMenuItem('Start here', href="https://coda.io/d/GEMS_dl7TPWND5QI/Start-here_suoQr#_lu7DY"),
                                                                dbc.DropdownMenuItem('GEMS', href="https://coda.io/d/GEMS_dl7TPWND5QI/GEMS_sudWp#_lu1pF"),
                                                                dbc.DropdownMenuItem('Upcoming GEMS', href="https://coda.io/d/GEMS_dl7TPWND5QI/Upcoming-GEMS_su3vn#_luLCV"),
                                                                dbc.DropdownMenuItem('Performance', href="https://coda.io/d/GEMS_dl7TPWND5QI/PERFORMANCE_suYBG#_lu6pO"),
                                                                dbc.DropdownMenuItem('GEM Sources', href="https://coda.io/d/GEMS_dl7TPWND5QI/Gem-Sources_su_ct#_lu2V3"),
                                                                dbc.DropdownMenuItem(divider=True),
                                                                dbc.DropdownMenuItem('Twitter', header=True),
                                                                dbc.DropdownMenuItem("@GEMSAlliance", href="https://twitter.com/GEMSAlliance"),
                                                                dbc.DropdownMenuItem('GEM Listing Tweets', href="https://twitter.com/search?q=(%23holdtight)%20(from%3AtokensFA%2C%20OR%20from%3AGEMSAlliance)&src=typed_query&f=live"),
                                                                dbc.DropdownMenuItem(divider=True),
                                                                dbc.DropdownMenuItem('Telegram', header=True),
                                                                dbc.DropdownMenuItem("GEMS Alliance", href='https://t.me/CryptoProjectsFA'),
                                                                dbc.DropdownMenuItem("GEMS Alliance - TA", href='https://t.me/joinchat/qyUKWrv1M1phNTk0'),
                                                                dbc.DropdownMenuItem("GEMS Alliance - OFFTOPIC", href='https://t.me/joinchat/42zS5ZoLxKZjMTU0'),
                                                            ],
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            style={'padding': 0},
                                            width='auto',
					),
				],
                                justify='between',
			),
		],  
		id='header',
		style={'margin-bottom': '0px', 'padding-bottom': 0, 'padding-top': 0},
	)


layout = generate_layout()


@app.callback(Output('page-title', 'children'),
    [Input('url', 'pathname')])
def update_title(pathname):
    if pathname in ["/", "/gems-overview"]:
        return 'Performance Overview'
    elif pathname == '/inspect-gem':
        return 'Inspect GEM'
    elif pathname == '/trends':
        return 'Trending Data'
    elif pathname == '/gmx-staking':
        return 'GMX Staking Data'
    elif pathname == '/gmx-chart':
        return 'GMX Uniswap Chart'
    else:
        return ''
