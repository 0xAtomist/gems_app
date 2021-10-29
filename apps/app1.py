import os, sys
from datetime import datetime
import json
import ast

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

import numpy as np
import pandas as pd
from collections import OrderedDict

from app import app, cache
from colours import *
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_extended_data, get_filtered_df, get_gem_markets

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
	'displaylogo': False,
        'displayModeBar': False,
}


def check_readings(gem, change):
	dff = get_data_recent(gem)

	if change == '1h':
		if dff['price_change_percentage_1h_in_currency'] > 0:
			health = 'Gainer'
		else:
			health = 'Loser'

	if change == '24h':
		if dff['price_change_percentage_24h_in_currency'] > 0:
			health = 'Gainer'
		else:
			health = 'Loser'

	if change == '7d':
		if dff['price_change_percentage_7d_in_currency'] > 0:
			health = 'Gainer'
		else:
			health = 'Loser'

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


def get_market_options():
	options = []
	gem_list = get_gem_list(master)
	variable_list = []
	for gem in gem_list:
                dff = get_gem_markets(gem)
                market_list = dff['name']
                for market in market_list:
                    variable_list.append(market)
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
    blank_df = pd.DataFrame({'symbol': ['No GEMS found'], variable: [0]})

    if not df.empty:
        df = df.sort_values(by=[variable])
        fig = px.bar(df, y=variable, x='symbol')
    else: 
        fig = px.bar(blank_df, y=variable, x='symbol')

    fig.update_traces(marker_color=color, marker=dict(line=dict(color=base_colours['black'])), hovertemplate=None)
    fig.update_xaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1)
    fig.update_yaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1)
    
    fig.update_layout(
        plot_bgcolor='#434343',
        paper_bgcolor=base_colours['card'],
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            tickfont=dict(family='Supermolot', size=11, color=base_colours['secondary_text']),
            tickangle=45,
        ),
        yaxis=dict(
            gridcolor=base_colours['secondary_text'],
            title=dict(text=''),
            tickfont=dict(family='Supermolot', size=13, color=base_colours['secondary_text']),
            ticksuffix='   ',
        ),
        showlegend=False,
        font={'color': base_colours['primary_text']},
        bargap=0.2,
        height=360,
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['text'])),
        hovermode='x',
    )

    return fig

def generate_pie_chart(gem_list, change):
    health_list = []
    for gem in gem_list:
        health = check_readings(gem, change)
        health_list.append(health)

    n_gainer = health_list.count('Gainer')
    n_loser = health_list.count('Loser')
    count_list = [1] * len(health_list)
    df = pd.DataFrame({'status': health_list, 'count': count_list})
    blank_df = pd.DataFrame({'status': ['No GEMS found'], 'count': [1]})

    if gem_list:
        fig = px.pie(df, values='count', names='status', hole=0.5, color='status',
            color_discrete_map={
                'Gainer': palette['green']['50'],
                'Loser': palette['red']['50'],
                'No GEMS found': base_colours['tf_accent'] 
            })
    else: 
        fig = px.pie(blank_df, values='count', names='status', hole=0.5, color='status',
            title=change,
            color_discrete_map={
                'Gainer': palette['green']['50'],
                'Loser': palette['red']['50'],
                'No GEMS found': base_colours['tf_accent']
            })

    fig.update_layout(
        plot_bgcolor=base_colours['card'],
        paper_bgcolor=base_colours['card'],
        margin={'l': 0, 'r': 0, 't': 10, 'b': 15},
        height=220,
        showlegend=False,
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['text'])),
    )

    fig.update_traces(
        hoverinfo='label+value',
        hovertemplate=None,
        textinfo='percent',
        marker=dict(line=dict(color=base_colours['tf_accent'], width=1.5)),
        textfont=dict(family='Supermolot', color=base_colours['text'], size=13),
    )

    return fig


def make_sparkline(srs):
    """
    :param df_wide: dataframe in "wide" format with the sparkline periods as columns
    :return: a series formatted for the sparkline fonts.
             Example:  '453{10,40,30,80}690'
    """
    spark_list = []
    idx = srs.index
    for i, item in enumerate(srs):
        item = ast.literal_eval(item)
        maxm = max(item['price'])
        minm = min(item['price'])
        short_item = item['price'][::12]
        spark_norm = (np.array(short_item) - minm) / (maxm - minm) * 100
        #spark_norm = np.array(short_item) / maxm * 100
        spark_norm = spark_norm.astype(int)
        start = str(round(item['price'][0], 2))
        end = str(round(item['price'][-1], 2))
        spark = '{' + str(spark_norm.tolist()).replace(' ', '')[1:-1] + '}'
        print(idx[i], spark)
        spark_list.append(spark)

    return pd.Series(spark_list, index=idx)


def generate_table_data(df):
    df['1h_col'] = df['1h_col']/100
    df['24h_col'] = df['24h_col']/100
    df['7d_col'] = df['7d_col']/100
    df['ath_change_percentage'] = df['ath_change_percentage']/100
    df['last_updated'] = pd.to_datetime(df['last_updated'], format='%Y-%m-%dT%H:%M:%S.%fZ').dt.strftime('%Y/%m/%d %H:%M')
    #print(df['sparkline_in_7d'])
    #df['sparkline'] = make_sparkline(df['sparkline_in_7d'])
    return df.to_dict('records')


def filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter, rewards_filter):
    gem_list = get_gem_list(master)
    gems = []
    tiers = []
    sectors = []
    markets = []
    rewards = []
    for option in get_gem_options():
        gems.append(option['value'])
    for option in get_options('Tier'):
        tiers.append(option['value'])
    for option in get_options('sector'):
        sectors.append(option['value'])
    for option in get_market_options():
        markets.append(option['value'])
    for option in get_options('Rewards'):
        rewards.append(option['value'])

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
                dff = get_gem_markets(gem)
                exchange_list = list(dff['name'])
                if market in exchange_list:
                    market_filter_list.append(gem)
    if not market_filter_list:
        market_filter_list = get_gem_list(master)

    rewards_filter_list= []
    for reward in rewards:
        if reward in rewards_filter:
            for gem in gem_list:
                if reward == master['gems'][gem]['Rewards']:
                    rewards_filter_list.append(gem)
    if not rewards_filter_list:
        rewards_filter_list = get_gem_list(master)

    all_present = set()

    for gem in get_gem_list(master):
        if gem in gem_filter_list and gem in tier_filter_list and gem in sector_filter_list and gem in market_filter_list and gem in rewards_filter_list:
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
								html.P('Gainers and Losers', style={'text-align': 'center'}),
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
											sm=4,
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
											sm=4,
											style={'padding': 0},
										),
										dbc.Col(
											[
												dcc.Graph(
												id="7d_pie",
													figure=generate_pie_chart(get_gem_list(master), '7d'),
													config=graph_config
												),
                                                                                                html.H2('7d', style={'textAlign': 'center', 'margin-bottom': 0})
											],
											sm=4,
											style={'padding': 0},
										),
									],
									style={'padding': 0},
									justify='center',
								)
							],
							className="pretty_container",
                                                        style={'height': 'auto', 'min-height': 380, 'padding-bottom': '10px'},
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
								options=get_market_options(),
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
							html.P("Filter by Rewards", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='rewards_filter',
								options=get_options('Rewards'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 0},
							),
						],
						className="pretty_container",
						style={'height': 'auto', 'min-height': 380}
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
						html.P('Data Overview', id='table_tooltip', style={'text-align': 'center'}),
                                                dbc.Tooltip(
                                                    'Table can be sorted by column and filtered using the dropdowns',
                                                    target='table_tooltip',
                                                    style={'font-family': 'Supermolot'}
                                                ),
						dash_table.DataTable(
							id="gems_table",
							sort_action='native',
                                                        sort_by=[{'column_id': '24h_col', 'direction': 'desc'}],
                                                        style_table={'overflowY': 'auto', 'border': '{} {} {}'.format('1px', 'solid', base_colours['cg_border'])},
							fixed_rows={'headers': True},
                                                        #style_as_list_view=True,
							columns=[
								{"name": ["Name"], "id": "name", "type": "text"},
								{"name": ["Ticker"], "id": "symbol", "type": "text"},
								{"name": ["Price"], "id": "current_price", "type": "numeric",
									"format": FormatTemplate.money(3)},
								{"name": ["1h"], "id": "1h_col", "type": "numeric",
									"format": FormatTemplate.percentage(1)},
								{"name": ["24h"], "id": "24h_col", "type": "numeric",
									"format": FormatTemplate.percentage(1)},
								{"name": ["7d"], "id": "7d_col", "type": "numeric",
									"format": FormatTemplate.percentage(1)},
								#{"name": ["Sparkline"], "id": "sparkline", "type": "text"},
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
								{"name": ["Market Cap / FDV Ratio"], "id": "mc_fdv_ratio", "type": "numeric",
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
								'background-color': base_colours['background'],
                                                                'color': base_colours['text'],
                                                                'font-size': 14,
								'font-weight': 'bold',
								'whiteSpace': 'normal',
								'height': 'auto',
                                                                'font-family': 'Supermolot',
							},
                                                        style_header_conditional=[
                                                                {'if': {'column_id': 'name'}, 'textAlign': 'left'},
                                                                {'if': {'column_id': 'symbol'}, 'textAlign': 'left'},
                                                        ],
							style_data_conditional=[
								#{'if': {'row_index': 'odd'},
								# 'backgroundColor': base_colours['card'],
								# 'color': base_colours['text']},
								#{'if': {'row_index': 'even'},
								# 'backgroundColor': base_colours['alt_row'],
								# 'color': base_colours['text']},
								{'if': {'column_id': 'name'}, 'color': base_colours['text']},
								{'if': 
									{
										'filter_query': '{rewards} = No or {rewards} = Negligible',
										'column_id': 'name'
									},
									'color': palette['green']['50']
								},
								{'if': 
									{
										'filter_query': '{rewards} = Yes',
										'column_id': 'name'
									},
									'color': palette['red']['50']
								},
								{'if': 
									{
										'filter_query': '{1h_col} > 0',
										'column_id': '1h_col'
									},
									'color': palette['green']['50']
								},
								{'if': 
									{
										'filter_query': '{24h_col} > 0',
										'column_id': '24h_col'
									},
									'color': palette['green']['50']
 
								},
								{'if': 
									{
										'filter_query': '{7d_col} > 0',
										'column_id': '7d_col'
									},
									'color': palette['green']['50']
								},
								{'if': 
									{
										'filter_query': '{1h_col} < 0',
										'column_id': '1h_col'
									},
									'color': palette['red']['50']
								},
								{'if': 
									{
										'filter_query': '{24h_col} < 0',
										'column_id': '24h_col'
									},
									'color': palette['red']['50']
								},
								{'if': 
									{
										'filter_query': '{7d_col} < 0',
										'column_id': '7d_col'
									},
									'color': palette['red']['50']
								},
                                                                {'if': {'state': 'active'},
                                                                        'backgroundColor': '#1f9990',
                                                                        'border': '1px solid #30d5c8',
                                                                        'color': '#ffffff',
                                                                },
							],
							style_cell={
                                                                'background-color': base_colours['cg_bg'],
                                                                'color': base_colours['cg_cell'],
                                                                'font-family': "sans-serif", 
                                                                'font-size': 13,
                                                                'border': '{} {} {}'.format('1px', 'solid', base_colours['cg_border']),
								'height': 'auto',
                                                                'whiteSpace': 'normal',
                                                                'padding': '10px',
                                                        },
							style_cell_conditional=[
                                                                {'if': {'column_id': 'sparkline'},
                                                                    'font-family': 'Sparks-Dotline-Medium',
                                                                    'fontSize': 24,
                                                                    'padding': '0px',
                                                                    'padding-top': '5px',
                                                                    #'max-width': '50px',
                                                                },
                                                                {'if': {'column_id': 'name'},
                                                                    'min-width': '80px',
                                                                    'max-width': '140px',
                                                                    'textAlign': 'left',
                                                                    'fontSize': 14,
                                                                    'fontWeight': 'bold',
                                                                    'font-family': 'Supermolot'},
                                                                {'if': {'column_id': 'symbol'},
                                                                    'textAlign': 'left',
                                                                    'fontSize': 14,
                                                                    'font-family': 'Supermolot'},
								{'if': {'column_id': 'mc_fdv_ratio'}, 'min-width': '100px'},
								{'if': {'column_id': '20x'}, 'min-width': '60px'},
								{'if': {'column_id': '50x'}, 'min-width': '60px'},
								{'if': {'column_id': 'gem_usd_x'}, 'min-width': '90px'},
								{'if': {'column_id': 'gem_btc_x'}, 'min-width': '90px'},
								{'if': {'column_id': 'last_updated'}, 'min-width': '70px'},
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
                                                    html.P('ATH GEM/USD Multiple', id='ath_gemusd_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('From date of GEMS Alliance tweet', target='ath_gemusd_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="ath_gemusd_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'ath_gem_usd_x', dash_green),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
                                                        html.P('ATH GEM/BTC Multiple', id='ath_gembtc_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('From date of GEMS Alliance tweet', target='gembtc_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="ath_gembtc_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'ath_gem_btc_x', yellow),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
				style={'padding': 0}
				),
			]
		),
		dbc.Row(
			[
				dbc.Col(
					html.Div(
						[
                                                    html.P('Current GEM/USD Multiple', id='gemusd_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('From date of GEMS Alliance tweet', target='gemusd_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="gemusd_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'gem_usd_x', dash_green),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
                                                        html.P('Current GEM/BTC Multiple', id='gembtc_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('From date of GEMS Alliance tweet', target='gembtc_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="gembtc_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'gem_btc_x', yellow),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
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
                                                        dbc.Tooltip('Retracement of the Current Price relative to the All Time High Price', target='athretrace_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="athretrace_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'ath_change_percentage', coral),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
                                                        html.P('Market Cap / FDV Ratio', id='mcfdv_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('Market Cap / FDV Ratio shows the amount of circulating supply relative to the total supply', target='mcfdv_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="mcfdv_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'mc_fdv_ratio', teal),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
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
                                                        dbc.Tooltip('Market Cap = Current Price * Circulating Supply', target='mc_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="mc_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'market_cap', magenta),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
				style={'padding': 0}
				),
				dbc.Col(
					html.Div(
						[
                                                        html.P('Fully Diluted Value (USD)', id='fdv_tooltip', style={'text-align': 'center', 'cursor': 'pointer'}), 
                                                        dbc.Tooltip('Fully Diluted Value = Current Price * Total Supply', target='fdv_tooltip', style={'font-family': 'Supermolot'}),
							dcc.Graph(
								id="fdv_bar",
								figure=generate_bar_chart(get_filtered_df(get_gem_list(master)), 'fdv_tot', blue),
								config=graph_config
							),
						],
						className="pretty_container",
						style={'height': 'auto'}
					),
				xl=6,
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
            Input('market_filter', 'value'),
            Input('rewards_filter', 'value')])
@cache.memoize(timeout=20)
def update_filter_store(gem_filter, tier_filter, sector_filter, market_filter, rewards_filter):
    if not gem_filter and not tier_filter and not sector_filter and not market_filter and not rewards_filter:
        filtered_json = json.dumps(get_gem_list(master))
        return filtered_json
    else:
        filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter, rewards_filter)
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


@app.callback(Output('ath_gemusd_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_ath_gemusd_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'ath_gem_usd_x', dash_green)


@app.callback(Output('ath_gembtc_bar', 'figure'),
	[Input('filter-store', 'data'),
	    Input('live-interval', 'n_intervals')])
@cache.memoize(timeout=20)
def update_ath_gembtc_bar(filtered_json, n_intervals):
    filtered_gem_list = json.loads(filtered_json)
    df = get_filtered_df(filtered_gem_list)
    return generate_bar_chart(df, 'ath_gem_btc_x', yellow)


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


