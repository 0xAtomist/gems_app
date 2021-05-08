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

from app import app, cache
from colours import *
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_extended_data, get_filtered_df

master = get_gem_info()

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


def generate_bar_chart(df, variable, color):
    if not df.empty:
        df = df.sort_values(by=[variable])
        data = [
            go.Bar(
                x=df['symbol'],
                y=df[variable],
                marker={'color': color},
                hoverinfo='x+y',
                #textinfo='percent',
            ),
        ]

    else: 
        data = [
            go.Bar(
                x=[0,0,0],
                y=[0,0,0],
                marker={'color': grey},
                text=['No Gems Found', 'No Gems Found', 'No Gems Found'],
            )
        ]

    figure={
        'data': data,
        'layout':
            go.Layout(
                #title='Gem 24h Overview',
                margin={'l': 40, 'r': 20, 't': 10, 'b': 50},
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


def generate_table_data(df):
    df['1h_col'] = df['1h_col']/100
    df['24h_col'] = df['24h_col']/100
    df['7d_col'] = df['7d_col']/100
    df['ath_change_percentage'] = df['ath_change_percentage']/100
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%dT%H:%M:%S.%fZ').dt.strftime('%Y/%m/%d %H:%M')
    return df.to_dict('records')
		
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

	return list(filtered_gem_list)


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
                                                        sort_by=[{'column_id': '24h_col', 'direction': 'desc'}],
							#style_table={'height': '2000px', 'overflowY': 'visible'},
							fixed_rows={'headers': True}, #'data': 0},
							columns=[
								{"name": ["Name"], "id": "name", "type": "text"},
								{"name": ["Ticker"], "id": "symbol", "type": "text"},
								{"name": ["Price"], "id": "current_price", "type": "numeric",
									"format": FormatTemplate.money(3)},
								{"name": ["1h"], "id": "1h_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["24h"], "id": "24h_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["7d"], "id": "7d_col", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								#{"name": ["Sparkline"], "id": "sparkline_col", "type": "numeric"},
								{"name": ["Market Cap"], "id": "market_cap", "type": "numeric",
									"format": Format(
										precision=0,
										scheme=Scheme.fixed,
										group=Group.yes, 
										groups=3, 
										symbol=Symbol.yes, 
										symbol_prefix='$'
									)
								},
								#{"name": ["FDV (Max Supply)"], "id": "fdv_max_col", "type": "numeric",
								#	"format": FormatTemplate.money(0)},
								{"name": ["FDV (Total Supply)"], "id": "fdv_tot", "type": "numeric",
									"format": Format(
										precision=0,
										scheme=Scheme.fixed,
										group=Group.yes, 
										groups=3, 
										symbol=Symbol.yes, 
										symbol_prefix='$'
									)
								},
								{"name": ["Market Cap/ FDV Ratio"], "id": "mc_fdv_ratio", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["Volume"], "id": "total_volume", "type": "numeric",
									"format": FormatTemplate.money(0)},
                                                                {"name": ["GEM/ USD Multiple"], "id": "gem_usd_x", "type": "numeric", "format": Format(precision=2)},
								{"name": ["GEM/ BTC Multiple"], "id": "gem_btc_x", "type": "numeric", "format": Format(precision=2)},
								{"name": ["20X Target"], "id": "20x", "type": "numeric",
									"format": FormatTemplate.money(1)},
								{"name": ["50X Target"], "id": "50x", "type": "numeric",
									"format": FormatTemplate.money(1)},
								{"name": ["ATH"], "id": "ath", "type": "numeric",
									"format": FormatTemplate.money(3)},
								{"name": ["ATH Retrace"], "id": "ath_change_percentage", "type": "numeric",
									"format": FormatTemplate.percentage(2)},
								{"name": ["Last Updated"], "id": "last_updated", "type": "numeric"},
							],
							data=generate_table_data(get_filtered_df(get_gem_list(master))),
							style_header={
								'text-align': 'right',
								'background-color': 'rgb(230, 230, 230)',
                                                                #'font-size': '14',
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
							style_cell={"font-family": "sans-serif", "font-size": 12}, #, 'border': '1px solid lightgrey'},
							style_cell_conditional=[
                                                                {'if': {'column_id': 'name'}, 'textAlign': 'left', 'fontWeight': 'bold', 'max-width': '120px'},
                                                                {'if': {'column_id': 'symbol'}, 'textAlign': 'left', 'fontWeight': 'bold'},
								{'if': {'column_id': 'mc_fdv_ratio'}, 'min-width': '80px'},
								{'if': {'column_id': '20x'}, 'min-width': '60px'},
								{'if': {'column_id': '50x'}, 'min-width': '60px'},
								{'if': {'column_id': 'gem_usd_x'}, 'min-width': '60px'},
								{'if': {'column_id': 'gem_btc_x'}, 'min-width': '60px'},
								{'if': {'column_id': 'last_updated'}, 'width': '70px'},
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
                                                        html.P('GEM/USD Multiple', id='gemusd_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('From date of GEMS Alliance tweet', target='gemusd_tooltip'),
							dcc.Graph(
								id="gemusd_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'gem_usd_x', dash_green),
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
                                                        html.P('GEM/BTC Multiple', id='gembtc_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('From date of GEMS Alliance tweet', target='gembtc_tooltip'),
							dcc.Graph(
								id="gembtc_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'gem_btc_x', yellow),
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
                                                        html.P('ATH Retrace (%)', id='athretrace_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('Retracement of the Current Price relative to the All Time High Price', target='athretrace_tooltip'),
							dcc.Graph(
								id="athretrace_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'ath_change_percentage', coral),
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
                                                        html.P('Market Cap / FDV Ratio', id='mcfdv_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('Market Cap / FDV Ratio shows the amount of circulating supply relative to the total supply', target='mcfdv_tooltip'),
							dcc.Graph(
								id="mcfdv_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'mc_fdv_ratio', teal),
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
                                                        html.P('Market Cap (USD)', id='mc_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('Market Cap = Current Price * Circulating Supply', target='mc_tooltip'),
							dcc.Graph(
								id="mc_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'market_cap', magenta),
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
                                                        html.P('Fully Diluted Value (USD)', id='fdv_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('Fully Diluted Value = Current Price * Total Supply', target='fdv_tooltip'),
							dcc.Graph(
								id="fdv_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'fdv_tot', blue),
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


@app.callback(Output('filter-store', 'data'),
	[Input('gem_filter', 'value'),
	    Input('tier_filter', 'value'),
	    Input('sector_filter', 'value'),
            Input('market_filter', 'value')])
@cache.memoize(timeout=20)
def update_filter_store(gem_filter, tier_filter, sector_filter, market_filter):
    if not gem_filter and not tier_filter and not sector_filter and not market_filter:
        filtered_json = json.dumps(get_gem_list(master))
        return filtered_json
    else:
        filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
        filtered_json = json.dumps(filtered_gem_list)
        return filtered_json


@app.callback(Output('gems_table', 'data'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_table(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_table_data(df)


@app.callback(Output('1h_pie', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_1h_pie(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    return generate_pie_chart(filtered_gem_list, '1h')


@app.callback(Output('24h_pie', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_24h_pie(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    return generate_pie_chart(filtered_gem_list, '24h')


@app.callback(Output('7d_pie', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_7d_pie(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    return generate_pie_chart(filtered_gem_list, '7d')


@app.callback(Output('gemusd_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_gemusd_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'gem_usd_x', dash_green)


@app.callback(Output('gembtc_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_gembtc_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'gem_btc_x', yellow)


@app.callback(Output('athretrace_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_athretrace_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'ath_change_percentage', coral)


@app.callback(Output('mcfdv_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_mcfdv_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'mc_fdv_ratio', teal)


@app.callback(Output('mc_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_mc_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'market_cap', magenta)


@app.callback(Output('fdv_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_fdv_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'fdv_tot', blue)

