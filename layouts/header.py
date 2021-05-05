import os, sys
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from datetime import timedelta
from dash.dependencies import Input, Output, State
from collections import OrderedDict

from app import app
from app.data_functions import get_gem_info, get_gem_list, get_data_recent, get_slider

# Get location info
master = get_gem_info()


def get_time_today():
	return int(pd.Timestamp.today().timestamp() + timedelta(days=1).total_seconds())


def generate_layout():
	return html.Div(
		[
			dcc.Interval(id='live-interval', interval=1*60*1000, n_intervals=0),
			dbc.Row(
				[
					dbc.Col(
						html.Img(
							#src=app.get_asset_url(),#"lcm_logo_medium.png"),
							style={
								'height': 'auto',
								'max-width': '100%',
								'width': 250,
								'margin-left': 5,
							},
							className='hidden-logo-sm',
							id='logo-head',
						),
						sm=4,
						style={'padding': 0},
					),
					dbc.Col(
						[
							html.H3(
								'GEMS Alliance',
								style={'margin-bottom': 0, 'text-align': 'center'},
							),
							html.H5(
								'GEMS Overview',
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
									html.A(
										dbc.Button(
											'Home',
											id='home-button',
											className="mr-1",
											color="info",
											style={'margin': 10}
										),
#                                        href='https://fueldashboard.lcmenvironmental.com',
									),
									html.A(
										dbc.Button(
											'Logout',
											id='logout-button',
											className="mr-1",
											color="danger",
											style={'margin': 10},
										),
#                                        href='https://fueldashboard.lcmenvironmental.com/logout',
									)
								],
								style={'text-align': 'right', 'margin-right': 10},
							),
						],
						sm=4,
						style={'padding': 0},
					),
				],
			),
			dbc.Row(
				dbc.Col(
					[
						html.Div(
							[
#                                dcc.Dropdown(
#                                    options=get_location_options(),
#                                    id='location-dropdown',
#                                    value=get_pub_list(pubs)[0],
#                                    placeholder='Change Selected Site',
#                                    className='m-1',
#                                ),
							],
							style={'float': 'right', 'width': '100%'},
						),
					],
					xl=7,
					style={'padding': 0, 'margin-left': 10, 'margin-right': 10},
				),
				justify='end',
			),
			dbc.Row(
				[
					dbc.Col(
						html.H6('Select Date Range: ', style={'text-align': 'left', 'margin-top': 15, 'padding-left': 0}),
						width=2,
					),
					dbc.Col(
						html.Div(
							[
								dcc.RangeSlider(
									id='date-slider',
									min=get_slider(get_gem_list(master)[0])[0],
									max=get_time_today(),
									step=86400,
									value=[get_time_today() - timedelta(days=30).total_seconds(), get_time_today()],
									marks=get_slider(get_gem_list(master)[0])[1],
									pushable=1,
									allowCross=False,
									updatemode='mouseup'
								),
							],
							style={'padding-bottom': 40, 'padding-top': 15, 'padding-right': 15},
						),
						width=10,
					),
				],
				#justify='center',
				id='slider-div',
				className='pretty_container pr-3',
				style={'padding': 0, 'margin-bottom': 0, 'display': 'none'},
			),
			dbc.Row(
				[
					dbc.Col(
						dbc.Row(
							[
								html.H6('Active Gem: ', style={'margin': 5}),
								html.P(id='active-gem', style={'margin-top': 3}),
							],
							className="pretty_container",
							style={'padding': 0, 'padding-top': 10, 'padding-left': 5, 'min-height': 50, 'height': 'auto'},
						),
						lg=6,
						style={'padding': 0}
					),
					dbc.Col(
						dbc.Row(
							[
								html.H6(id='reading-type', style={'margin': 5}),
								html.P(id='reading-time', style={'margin-top': 3}),
							],
							className="pretty_container",
							style={'padding': 0, 'padding-top': 10, 'padding-left': 5, 'min-height': 50, 'height': 'auto'},
						),
						lg=6,
						style={'padding': 0},
					),
				],
				id='active-gem-div',
				style={'padding': 0, 'display': 'none'},
			),
		],  
		id='header',
		style={'margin-bottom': '0px', 'padding-bottom': 0, 'padding-top': 0},
	)


layout = generate_layout()

