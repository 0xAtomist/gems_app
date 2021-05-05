import os, sys
from datetime import datetime
import json

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import pandas as pd
import dash_table.FormatTemplate as FormatTemplate
from dash_table.Format import Format, Scheme, Sign, Symbol, Group
import plotly.graph_objs as go
from collections import OrderedDict
from dash.dependencies import Input, Output, State

from app import app
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_extended_data

health_dict = {
	'gainer': green,
	'loser': red,
}

yellow = '#f4a522'
blue = '#6092cd'
dash_green = '#61b546'
magenta = '#aa4498'
coral = '#fd625e'
teal = '#01b8aa'
grey = '#d0d0d0'

# Functions
#mapbox_access_token = auth_conf['mapbox']['access token']

graph_config = {
	'modeBarButtonsToRemove': [
		'pan2d', 'lasso2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
		'hoverClosestCartesian','hoverCompareCartesian', 'toggleSpikelines', 'zoom2d', 
		'sendDataToCloud', 'hoverClosestPie', 'toggleHover', 'resetViewMapbox'
	],
	'displaylogo': False
}


def check_readings(gem, change):
	dff = get_data_recent(gem)

	if change == '1h':
		if dff['price_change_percentage_1h_in_currency'] > 0:
			health = 'gainer'
		else:
			health = 'loser'

	if change == '24h':
		if dff['price_change_percentage_24h_in_currency'] > 0:
			health = 'gainer'
		else:
			health = 'loser'

	if change == '7d':
		if dff['price_change_percentage_7d_in_currency'] > 0:
			health = 'gainer'
		else:
			health = 'loser'

	return health


def get_options(variable):
	options = []
	gem_list = get_gem_list(master)
	variable_list = []
	for gem in gem_list:
		variable_list.append(master['gems'][gem][variable])
	df = pd.DataFrame(data={'label': variable_list, 'value': variable_list})
	df = df.sort_values('label')
	df = df.drop_duplicates()
	for i in df.index:
		options.append({'label': df.loc[i]['label'], 'value': df.loc[i]['value']})
	return options


def get_gem_options():
	gem_options = []
	gem_list = get_gem_list(master)
	ticker_list = []
	for gem in gem_list:
		ticker_list.append(master['gems'][gem]['symbol'])
	df = pd.DataFrame(data={'ticker': ticker_list, 'gem': gem_list})
	df = df.sort_values('ticker')
	for i in df.index:
		gem_options.append({'label': df.loc[i]['ticker'], 'value': df.loc[i]['gem']})
	return gem_options


def gain_table_data(gem_list):
	change_list = []
	loss_list = []
	gain_list = []
	for gem in gem_list:
		change = get_24h_change(gem)
		change_list.append(change)
	for i, change in enumerate(change_list):
		if change < 0:
			loss_list.append(gem_list[i])
		elif change > 0:
			gain_list.append(gem_list[i])

	data_dict = OrderedDict([
		("gem_col", []),
		("change_col", [])
	])
	for gem in sorted(loss_list):
		gem_info = master['gems'][gem]
		data_dict['gem_col'].append(gem)
		data_dict['change_col'].append(get_24h_change(gem))

	for gem in sorted(gain_list):
		gem_info = master['gems'][gem]
		data_dict['gem_col'].append(gem)
		data_dict['change_col'].append(get_24h_change(gem))

	df = pd.DataFrame(data_dict)
	return df

ef generate_table_data(gem_list):
	data_dict = OrderedDict([
		("name_col", []),
		("symbol_col", []),
		("price_col", []),
		("1h_col", []),
		("24h_col", []),
		("7d_col", []),
		("market_cap_col", []),
		("fdv_max_col", []),
		("fdv_tot_col", []),
		("mc_fdv_ratio_col", []),
		("volume_col", []),
		("20x_col", []),
		("50x_col", []),
		("ath_col", []),
		("ath_retrace_col", []),
		("datetime_col", []),
	])

	for gem in sorted(gem_list): 
		recent_data = get_data_recent(gem)
		extended_data = get_extended_data(gem)
		gem_info = master['gems'][gem]

		data_dict['symbol_col'].append(gem_info['symbol'])
		data_dict['name_col'].append(recent_data['name'])

		if recent_data['last_updated'] == 0:
			data_dict['datetime_col'].append(0)
		else:
			data_dict['datetime_col'].append(
				datetime.strftime(datetime.strptime(recent_data['last_updated'],'%Y-%m-%dT%H:%M:%S.%fZ'), '%d/%m/%y %H:%M')
			)

		data_dict['price_col'].append(recent_data['current_price'])
		data_dict['1h_col'].append(recent_data['price_change_percentage_1h_in_currency']/100)
		data_dict['24h_col'].append(recent_data['price_change_percentage_24h_in_currency']/100)
		data_dict['7d_col'].append(recent_data['price_change_percentage_7d_in_currency']/100)
		data_dict['market_cap_col'].append(recent_data['market_cap'])
		data_dict['fdv_max_col'].append(recent_data['fully_diluted_valuation'])
		data_dict['fdv_tot_col'].append(extended_data['fdv_tot'])
		data_dict['mc_fdv_ratio_col'].append(extended_data['mc_fdv_ratio'])
		data_dict['volume_col'].append(recent_data['total_volume'])
		data_dict['20x_col'].append(extended_data['20x'])
		data_dict['50x_col'].append(extended_data['50x'])
		data_dict['ath_col'].append(recent_data['ath'])
		data_dict['ath_retrace_col'].append(recent_data['ath_change_percentage']/100)

	df = pd.DataFrame(data_dict)
	return df



def get_urgent_list(urgency, gem_list):
	urgent_list = []
	for gem in gem_list:
		gem_info = master['gems'][gem]
		health = check_readings(gem)
		if health == urgency:
			urgent_list.append(gem_info['symbol'])
	return sorted(urgent_list)


def n_urgent_alert(urgency, gem_list):
	health_list = []
	for gem in gem_list:
		health = check_readings(gem)
		health_list.append(health)
	return health_list.count(urgency)


def generate_bar_chart(gem_list, source, variable, color):
	if gem_list:
		if source == 'ext':
			variable_list = []
			ticker_list = []
			for gem in sorted(gem_list):
				ticker_list.append(get_data_recent(gem)['symbol'])
				variable_list.append(get_extended_data(gem)[variable])
			df = pd.DataFrame(data={'gems': ticker_list, variable: variable_list})
			df = df.sort_values(variable)

		elif source == 'api':
			variable_list = []
			ticker_list = []
			for gem in sorted(gem_list):
				ticker_list.append(get_data_recent(gem)['symbol'])
				variable_list.append(get_data_recent(gem)[variable])
			df = pd.DataFrame(data={'gems': ticker_list, variable: variable_list})
			df = df.sort_values(variable)
			print(df)

		data = [
			go.Bar(
				x=df['gems'],
				y=df[variable],
				marker={'color': color},
				hoverinfo='x+y',
				#textinfo='percent',
			),
		]

	else: 
		data = [
			go.bar(
				x=[0,0,0],
				y=[0,0,0],
				marker={'color': grey},
				text=['No Gems Found', 'No Gems Found', 'No Gems Found'],
				hoverinfo='text+value',
				#textinfo='percent',
			)
		]

	figure={
		'data': data,
		'layout':
			go.Layout(
				#title='Gem 24h Overview',
				margin={'l': 40, 'r': 20, 't': 0, 'b': 50},
				#legend={'font': {'size': 10}, 'orientation': 'h'},
				#autosize=True,
				xaxis=dict(tickangle=45),
				height=300,
				#width='auto',
				showlegend=False,
			),
	}

	return figure

def generate_pie_chart(gem_list, change):
	health_list = []
	for gem in gem_list:
		health = check_readings(gem, change)
		health_list.append(health)

	n_gainer = health_list.count('gainer')
	n_loser = health_list.count('loser')

	if gem_list:
		data = [
			go.Pie(
				values=[n_gainer, n_loser],
				#labels=['Gainers', 'Losers'],
				hole=0.5,
				marker={'colors': [green, red]},
				text=['Gainers', 'Losers'],
				hoverinfo='text+value+percent',
				textinfo='percent',
			),
		]
	else: 
		data = [
			go.Pie(
				values=[100],
				labels=['No Gems Found'],
				hole=0.5,
				marker={'colors': ['#d0d0d0']},
				text=['No Gems Found'],
				hoverinfo='text',
				textinfo='percent',
			)
		]

	figure={
		'data': data,
		'layout':
			go.Layout(
				title='Gem 24h Overview',
				margin={'l': 15, 'r': 0, 't': 0, 'b': 15},
				#legend={'font': {'size': 10}, 'orientation': 'h'},
				#autosize=True,
				height=200,
				#width='auto',
				showlegend=False,
			),
	}

	return figure

		
def filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter):
	gem_list = get_gem_list(master)
	gems = []
	tiers = []
	sectors = []
	markets = []
	for option in get_gem_options():
		gems.append(option['value'])
	for option in get_options('Tier'):
		tiers.append(option['value'])
	for option in get_options('sector'):
		sectors.append(option['value'])
	for option in get_options('market'):
		markets.append(option['value'])

	filtered_gem_list = []

	gem_filter_list = []
	for f_gem in gems:
		if f_gem in gem_filter:
			for gem in gem_list:
				if f_gem == gem:
					gem_filter_list.append(gem)
	if not gem_filter_list:
		gem_filter_list = get_gem_list(master)
	
	tier_filter_list = []
	for tier in tiers:
		if tier in tier_filter:
			for gem in gem_list:
				if tier == master['gems'][gem]['Tier']:
					tier_filter_list.append(gem)
	if not tier_filter_list:
		tier_filter_list = get_gem_list(master)

	sector_filter_list = []
	for sector in sectors:
		if sector in sector_filter:
			for gem in gem_list:
				if sector == master['gems'][gem]['sector']:
					sector_filter_list.append(gem)
	if not sector_filter_list:
		sector_filter_list = get_gem_list(master)

	market_filter_list= []
	for market in markets:
		if market in market_filter:
			for gem in gem_list:
				if market == master['gems'][gem]['market']:
					market_filter_list.append(gem)
	if not market_filter_list:
		market_filter_list = get_gem_list(master)

	all_present = set()

	for gem in get_gem_list(master):
		if gem in gem_filter_list and gem in tier_filter_list and gem in sector_filter_list and gem in market_filter_list:
			all_present.add(gem)

	filtered_gem_list = all_present

	return set(filtered_gem_list)


layout = html.Div(
	[
		dbc.Row(
			[
				dbc.Col(
					[
						html.Div(
							[
								html.P('Status Overview', style={'text-align': 'center'}),
								dbc.Row(
									[
										dbc.Col(
											[
												dcc.Graph(
												id="1h_pie",
													figure=generate_pie_chart(get_gem_list(master), '1h'),
													config=graph_config
												),
												html.H3('1h', style={'textAlign': 'center'})
											],
											width=4,
											style={'padding': 0},
											align='center',
										),
										dbc.Col(
											[
												dcc.Graph(
												id="24h_pie",
													figure=generate_pie_chart(get_gem_list(master), '24h'),
													config=graph_config,
												),
												html.H2('24h', style={'textAlign': 'center'})
											],
											width=4,
											style={'padding': 0},
										),
										dbc.Col(
											[
												dcc.Graph(
												id="7d_pie",
													figure=generate_pie_chart(get_gem_list(master), '7d'),
													config=graph_config
												),
												html.H2('7d', style={'textAlign': 'center'})
											],
											width=4,
											style={'padding': 0},
										),
									],
									style={'padding': 0},
									justify='center',
								)
							],
							className="pretty_container",
							style={'height': 'auto', 'min-height': 350},
						),
					],
					xl=8,
					style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
							html.P("Filter by Gem", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='gem_filter',
								options=get_gem_options(),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
							html.P("Filter by Market", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='market_filter',
								options=get_options('market'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
							html.P("Filter by Sector", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='sector_filter',
								options=get_options('sector'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
							html.P("Filter by Tier", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='tier_filter',
								options=get_options('Tier'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
						],
						className="pretty_container",
						style={'height': 'auto', 'min-height': 350}
					),
				xl=4,
				style={'padding': 0}
				),
			]
		),
		dbc.Row(
			dbc.Col(
				html.Div(
					[
						html.P('Data Overview', style={'text-align': 'center'}),
						dash_table.DataTable(
							id="gems_table",
							sort_action='native',
							#style_table={'height': '1000px', 'overflowY': 'visible'},
							fixed_rows={'headers': True}, #'data': 0},
							columns=[
								{"name": ["Name"], "id": "name_col", "type": "text"},
								{"name": ["Ticker"], "id": "symbol_col", "type": "text"},
								{"name": ["Price"], "id": "price_col", "type": "numeric",
									"format": FormatTemplate.money(3)},
								{"name": ["1h"], "id": "1h_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["24h"], "id": "24h_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["7d"], "id": "7d_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								#{"name": ["Sparkline"], "id": "sparkline_col", "type": "numeric"},
								{"name": ["Market Cap"], "id": "market_cap_col", "type": "numeric",
									"format": Format(
										precision=0,
										scheme=Scheme.fixed,
										group=Group.yes, 
										groups=3, 
										symbol=Symbol.yes, 
										symbol_prefix='$'
									)
								},
								{"name": ["FDV (Max Supply)"], "id": "fdv_max_col", "type": "numeric",
									"format": FormatTemplate.money(0)},
								{"name": ["FDV (Total Supply)"], "id": "fdv_tot_col", "type": "numeric",
									"format": Format(
										precision=0,
										scheme=Scheme.fixed,
										group=Group.yes, 
										groups=3, 
										symbol=Symbol.yes, 
										symbol_prefix='$'
									)
								},
								{"name": ["Market Cap/ FDV Ratio"], "id": "mc_fdv_ratio_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["Volume"], "id": "volume_col", "type": "numeric",
									"format": FormatTemplate.money(0)},
								{"name": ["20X Target"], "id": "20x_col", "type": "numeric",
									"format": FormatTemplate.money(1)},
								{"name": ["50X Target"], "id": "50x_col", "type": "numeric",
									"format": FormatTemplate.money(1)},
								{"name": ["ATH"], "id": "ath_col", "type": "numeric",
									"format": FormatTemplate.money(3)},
								{"name": ["ATH Retrace"], "id": "ath_retrace_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["Last Updated"], "id": "datetime_col", "type": "numeric"},
							],
							data=generate_table_data(get_gem_list(master)).to_dict('rows'),
							style_header={
								'text-align': 'left',
								'background-color': 'rgb(230, 230, 230)',
								'font-weight': 'bold',
								'whiteSpace': 'normal',
								'height': 'auto',
								#'border': '1px solid lightgrey',
							},
							style_data_conditional=[
								{'if': {'row_index': 'odd'},
								 'backgroundColor': 'rgb(248, 248, 248)',
								 'color': '#000000'},
								{'if': {'row_index': 'even'},
								 'backgroundColor': '#ffffff',
								 'color': '#000000'},
								{'if': 
									{
										'filter_query': '{1h_col} > 0',
										'column_id': '1h_col'
									},
									'color': 'green'
								},
								{'if': 
									{
										'filter_query': '{24h_col} > 0',
										'column_id': '24h_col'
									},
									'color': 'green'
								},
								{'if': 
									{
										'filter_query': '{7d_col} > 0',
										'column_id': '7d_col'
									},
									'color': 'green'
								},
								{'if': 
									{
										'filter_query': '{1h_col} < 0',
										'column_id': '1h_col'
									},
									'color': 'red'
								},
								{'if': 
									{
										'filter_query': '{24h_col} < 0',
										'column_id': '24h_col'
									},
									'color': 'red'
								},
								{'if': 
									{
										'filter_query': '{7d_col} < 0',
										'column_id': '7d_col'
									},
									'color': 'red'
								}
							],
							style_cell={"font-family": "sans-serif", "font-size": 11}, #, 'border': '1px solid lightgrey'},
							style_cell_conditional=[
								{'if': {'column_id': 'name_col'}, 'textAlign': 'left', 'max-width': '140px'},
								{'if': {'column_id': 'symbol_col'}, 'textAlign': 'left'},
								{'if': {'column_id': 'mc_fdv_ratio_col'}, 'min-width': '60px'},
							],
						)
					],
					className="pretty_container",
					style={'height': 'auto'}
				),
			width=12,
			style={'padding': 0}
			),
		),
		dbc.Row(
			[
				dbc.Col(
					html.Div(
						[
														html.P('GEM/USD Multiple', style={'text-align': 'center'}), 
							dcc.Graph(
								id="gemusd_bar",
								figure=generate_bar_chart(get_gem_list(master), 'ext', 'gem_usd_x', dash_green),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				width=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
														html.P('GEM/BTC Multiple', style={'text-align': 'center'}), 
							dcc.Graph(
								id="gembtc_bar",
								figure=generate_bar_chart(get_gem_list(master), 'ext', 'gem_btc_x', yellow),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				width=6,
				style={'padding': 0}
				),
			]
		),
		dbc.Row(
			[
				dbc.Col(
					html.Div(
						[
														html.P('ATH Retrace', style={'text-align': 'center'}),  
							dcc.Graph(
								id="athretrace_bar",
								figure=generate_bar_chart(get_gem_list(master), 'api', 'ath_change_percentage', coral),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				width=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
														html.P('Market Cap / FDV Ratio', style={'text-align': 'center'}),   
							dcc.Graph(
								id="mcfdv_bar",
								figure=generate_bar_chart(get_gem_list(master), 'ext', 'mc_fdv_ratio', teal),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				width=6,
				style={'padding': 0}
				),
			]
		),
		dbc.Row(
			[
				dbc.Col(
					html.Div(
						[
														html.P('Market Cap', style={'text-align': 'center'}),   
							dcc.Graph(
								id="mc_bar",
								figure=generate_bar_chart(get_gem_list(master), 'api', 'market_cap', magenta),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				width=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
														html.P('Fully Diluted Value (Total)', style={'text-align': 'center'}),
							dcc.Graph(
								id="fdv_bar",
								figure=generate_bar_chart(get_gem_list(master), 'ext', 'fdv_tot', blue),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				width=6,
				style={'padding': 0}
				),
			]
		),
	],
	id='gems-overview-container',
)


@app.callback(Output('gems_table', 'data'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_table(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		df = generate_table_data(get_gem_list(master))
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		df = generate_table_data(filtered_gem_list)
	return df.to_dict('rows')


@app.callback(Output('1h_pie', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_1h_pie(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_pie_chart(get_gem_list(master), '1h')
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_pie_chart(filtered_gem_list, '1h')


@app.callback(Output('24h_pie', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_24h_pie(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_pie_chart(get_gem_list(master), '24h')
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_pie_chart(filtered_gem_list, '24h')


@app.callback(Output('7d_pie', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_7d_pie(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_pie_chart(get_gem_list(master), '7d')
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_pie_chart(filtered_gem_list, '7d')


@app.callback(Output('gemusd_bar', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_gemusd_bar(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_bar_chart(get_gem_list(master), 'ext', 'gem_usd_x', dash_green)
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_bar_chart(filtered_gem_list, 'ext', 'gem_usd_x', dash_green)


@app.callback(Output('gembtc_bar', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_gemusd_bar(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_bar_chart(get_gem_list(master), 'ext', 'gem_btc_x', yellow)
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_bar_chart(filtered_gem_list, 'ext', 'gem_btc_x', yellow)


@app.callback(Output('athretrace_bar', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_gemusd_bar(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_bar_chart(get_gem_list(master), 'api', 'ath_change_percentage', coral)
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_bar_chart(filtered_gem_list, 'api', 'ath_change_percentage', coral)


@app.callback(Output('mcfdv_bar', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_gemusd_bar(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_bar_chart(get_gem_list(master), 'ext', 'mc_fdv_ratio', teal)
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_bar_chart(filtered_gem_list, 'ext', 'mc_fdv_ratio', teal)


@app.callback(Output('mc_bar', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_gemusd_bar(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_bar_chart(get_gem_list(master), 'api', 'market_cap', magenta)
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_bar_chart(filtered_gem_list, 'api', 'market_cap', magenta)


@app.callback(Output('fdv_bar', 'figure'),
	[Input('gem_filter', 'value'),
		Input('tier_filter', 'value'),
		Input('sector_filter', 'value'),
		Input('market_filter', 'value'),
		Input('live-interval', 'n_intervals')])
def update_gemusd_bar(gem_filter, tier_filter, sector_filter, market_filter, n_intervals):
	if not gem_filter and not tier_filter and not sector_filter and not market_filter:
		return generate_bar_chart(get_gem_list(master), 'ext', 'fdv_tot', blue)
	else:
		filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
		return generate_bar_chart(filtered_gem_list, 'ext', 'fdv_tot', blue)
