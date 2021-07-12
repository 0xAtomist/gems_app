import os, sys
from datetime import datetime
import json
from datetime import date

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
from data_functions import get_gem_info, get_gem_list, get_data_recent, get_extended_data, get_filtered_df, get_chart_range_data

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

gem_style = []

for item in px.colors.qualitative.Pastel:
    gem_style.append([item, None])

for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dash'])
    
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dot'])


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


def generate_price_trend(gem_list, start_date, end_date):
    fig_range = go.Figure()
    for i, gem in enumerate(gem_list):
        symbol = master['gems'][gem]['symbol']
        dff = get_chart_range_data(gem, start_date, end_date)
        fig_range.add_trace(go.Scatter(x=dff['Datetime'], y=dff['relative_price'], name=symbol,
                            line=dict(color=gem_style[i][0], dash=gem_style[i][1])))
    fig_range.update_layout(
        plot_bgcolor='#363636',
        paper_bgcolor='#363636',
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            tickfont=dict(color='#b0b3b8'),
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor='#b0b3b8',
            title=dict(text='Relative Price'),
            tickfont=dict(color='#b0b3b8'),
            ticksuffix='   ',
        ),
        showlegend=True,
        font={'color': '#fff'},
        hoverlabel=dict(font=dict(color='#fff')),
        #hovermode='x',
        height=650,
        #width='auto',
    )
    return fig_range


def generate_market_cap_trend(gem_list, start_date, end_date):
    fig_range = go.Figure()
    for i, gem in enumerate(gem_list):
        symbol = master['gems'][gem]['symbol']
        dff = get_chart_range_data(gem, start_date, end_date)
        fig_range.add_trace(go.Scatter(x=dff['Datetime'], y=dff['market_caps'], name=symbol,
                            line=dict(color=gem_style[i][0], dash=gem_style[i][1])))
    fig_range.update_layout(
        plot_bgcolor='#363636',
        paper_bgcolor='#363636',
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            tickfont=dict(color='#b0b3b8'),
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor='#b0b3b8',
            title=dict(text='Market Cap'),
            tickfont=dict(color='#b0b3b8'),
            ticksuffix='   ',
            tickprefix='$',
        ),
        showlegend=True,
        font={'color': '#fff'},
        hoverlabel=dict(font=dict(color='#fff')),
        #hovermode='x',
        height=650,
        #width='auto',
    )
    return fig_range


def generate_mc_relative_trend(gem_list, start_date, end_date):
    fig_range = go.Figure()
    for i, gem in enumerate(gem_list):
        symbol = master['gems'][gem]['symbol']
        dff = get_chart_range_data(gem, start_date, end_date)
        fig_range.add_trace(go.Scatter(x=dff['Datetime'], y=dff['relative_cap'], name=symbol,
                            line=dict(color=gem_style[i][0], dash=gem_style[i][1])))
    fig_range.update_layout(
        plot_bgcolor='#363636',
        paper_bgcolor='#363636',
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            tickfont=dict(color='#b0b3b8'),
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor='#b0b3b8',
            title=dict(text='Relative Market Cap'),
            tickfont=dict(color='#b0b3b8'),
            ticksuffix='   ',
        ),
        showlegend=True,
        font={'color': '#fff'},
        hoverlabel=dict(font=dict(color='#fff')),
        #hovermode='x',
        height=650,
        #width='auto',
    )
    return fig_range


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


fig_price = generate_price_trend(get_gem_list(master), '2021-01-01', '2021-07-12')

fig_market_cap = generate_market_cap_trend(get_gem_list(master), '2021-01-01', '2021-07-12')


layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.P("Filter by Gem", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='gem_filter2',
								options=get_gem_options(),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
							html.P("Filter by Market", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='market_filter2',
								options=get_options('market'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
                                                    ],
                                                ),
                                            ],
                                            md=4,
                                            style={'padding-right': 10, 'padding-left': 10},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.P("Filter by Sector", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='sector_filter2',
								options=get_options('sector'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
							html.P("Filter by Tier", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='tier_filter2',
								options=get_options('Tier'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 0},
							),
                                                    ],
                                                ),
                                            ],
                                            md=4,
                                            style={'padding-right': 10, 'padding-left': 10},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
							html.P("Select Date Range of Trends", style={'margin-bottom': 2}),
                                                        dcc.DatePickerRange(
                                                            id='trend_date_picker',
                                                            display_format='DD-MMM-YYYY',
                                                            min_date_allowed=date(2020, 1, 1),
                                                            max_date_allowed=date.today(),
                                                            initial_visible_month=date.today(),
                                                            end_date=date.today(),
                                                            start_date='2021-01-01'
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            md={'width': 3, 'offset': 1},
                                            align='center',
                                        ),
                                    ],
                                    style={'padding-right': 10, 'padding-left': 10},
                                ),
                            ],
                            id='trending_ribbon',
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 60, 'padding': 10},
                        ),
                    ],
                    xl=12,
                    style={'padding': 0},
                ),
            ],
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.P('Market Cap', id='mc_trend_tip', style={'text-align': 'center'}),
                                dbc.Tooltip(
                                    'Dates are selectable and gems are filtered using the dropdowns',
                                    target='mc_trend_tip',
                                    style={'font-family': 'Supermolot'}
                                ),
                                dcc.Graph(id='trend_market_cap', figure=fig_market_cap, config=graph_config)
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 600},
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
                                html.P('Relative Price from Start Date', id='relative_price_tip', style={'text-align': 'center'}),
                                dbc.Tooltip(
                                    'The initial date from which the prices are relative to can be selected using the date picker',
                                    target='relative_price_tip',
                                    style={'font-family': 'Supermolot'}
                                ),
                                dcc.Graph(id='trend_price', figure=fig_price, config=graph_config)
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 600},
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
                                html.P('Relative Market Cap from Start Date', id='relative_mc_tip', style={'text-align': 'center'}),
                                dbc.Tooltip(
                                    'The initial date from which the market caps are relative to can be selected using the date picker',
                                    target='relative_mc_tip',
                                    style={'font-family': 'Supermolot'}
                                ),
                                dcc.Graph(id='trend_mc_relative', figure=fig_price, config=graph_config)
                            ],
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 600},
                        ),
                    ],
                    xl=12,
                    style={'padding': 0}
                ),
            ],
        ),
    ],
    id='trending-container',
)


@app.callback(Output('filter-trend', 'data'),
	[Input('gem_filter2', 'value'),
	    Input('tier_filter2', 'value'),
	    Input('sector_filter2', 'value'),
            Input('market_filter2', 'value')])
@cache.memoize(timeout=20)
def update_filter_trend(gem_filter, tier_filter, sector_filter, market_filter):
    if not gem_filter and not tier_filter and not sector_filter and not market_filter:
        filtered_json = json.dumps(get_gem_list(master))
        return filtered_json
    else:
        filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter)
        filtered_json = json.dumps(filtered_gem_list)
        return filtered_json


@app.callback(Output('trend_price', 'figure'),
	[Input('filter-trend', 'data'),
            Input('trend_date_picker', 'start_date'),
            Input('trend_date_picker', 'end_date')])
@cache.memoize(timeout=20)
def update_trend_price(filtered_json, start_date, end_date):
    filtered_gem_list = json.loads(filtered_json)
    return generate_price_trend(filtered_gem_list, start_date, end_date)


@app.callback(Output('trend_market_cap', 'figure'),
	[Input('filter-trend', 'data'),
            Input('trend_date_picker', 'start_date'),
            Input('trend_date_picker', 'end_date')])
@cache.memoize(timeout=20)
def update_trend_market_cap(filtered_json, start_date, end_date):
    filtered_gem_list = json.loads(filtered_json)
    return generate_market_cap_trend(filtered_gem_list, start_date, end_date)


@app.callback(Output('trend_mc_relative', 'figure'),
	[Input('filter-trend', 'data'),
            Input('trend_date_picker', 'start_date'),
            Input('trend_date_picker', 'end_date')])
@cache.memoize(timeout=20)
def update_trend_mc_relative(filtered_json, start_date, end_date):
    filtered_gem_list = json.loads(filtered_json)
    return generate_mc_relative_trend(filtered_gem_list, start_date, end_date)
