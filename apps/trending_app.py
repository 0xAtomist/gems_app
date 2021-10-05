import os, sys
from datetime import datetime, timedelta, date
import json

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

# Set line styles for the list of GEMS
gem_style = []
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, None, 'lines'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dash', 'lines'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dot', 'lines'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dashdot', 'lines'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, None, 'lines+markers'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dash', 'lines+markers'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dot', 'lines+markers'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dashdot', 'lines+markers'])


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


def generate_trend(gem_list, start_date, end_date, y_var, y_text, hover_temp):
    fig_range = go.Figure()
    for i, gem in enumerate(gem_list):
        symbol = master['gems'][gem]['symbol']
        dff = get_chart_range_data(gem, start_date, end_date)
        fig_range.add_trace(
            go.Scatter(
                x=dff['Datetime'], 
                y=dff[y_var], 
                name=symbol, 
                hovertemplate=hover_temp,
                mode=gem_style[i][2],
                line=dict(color=gem_style[i][0], dash=gem_style[i][1]),
                textfont=dict(family='Supermolot', color=base_colours['text'], size=13)
            )
        )
    fig_range.update_layout(
        plot_bgcolor='#434343',
        paper_bgcolor=base_colours['card'],
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor=base_colours['secondary_text'],
            title=dict(text=y_text),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            ticksuffix='   ',
            tickprefix='',
        ),
        showlegend=True,
        font={'color': base_colours['primary_text']},
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['black'])),
        hovermode='x',
        height=650,
        legend=dict(font=dict(family='Supermolot', color=base_colours['text']))
    )

    fig_range.update_xaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1) #, rangeslider_visible=True)
    fig_range.update_yaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1)

    return fig_range


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
    for option in get_options('market'):
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
                if market == master['gems'][gem]['market']:
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
                                            lg=4,
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
                                            lg=4,
                                            style={'padding-right': 10, 'padding-left': 10},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
							html.P("Filter by Rewards", style={'margin-bottom': 2}),
							dcc.Dropdown(
								id='rewards_filter2',
								options=get_options('Rewards'),
								multi=True,
								value=[],
								style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
							),
							html.P("Select Date Range of Trends", style={'margin-bottom': 2}),
                                                        dcc.DatePickerRange(
                                                            id='trend_date_picker',
                                                            display_format='DD-MMM-YYYY',
                                                            min_date_allowed=date(2020, 1, 1),
                                                            max_date_allowed=date.today(),
                                                            initial_visible_month=date.today()-timedelta(90),
                                                            end_date=date.today(),
                                                            start_date=date.today()-timedelta(90),
							    style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            lg=4,
                                            #align='center',
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
                                dcc.Graph(
                                    id='trend_market_cap',
                                    config=graph_config,
                                    figure=generate_trend(get_gem_list(master), datetime.strftime(date.today()-timedelta(90), '%Y-%m-%d'), datetime.strftime(date.today(), '%Y-%m-%d'), 'market_caps', 'Market Cap', '$%{y:,.0f}')
                                )
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
                                dcc.Graph(
                                    id='trend_price',
                                    config=graph_config,
                                    figure=generate_trend(get_gem_list(master), datetime.strftime(date.today()-timedelta(90), '%Y-%m-%d'), datetime.strftime(date.today(), '%Y-%m-%d'), 'relative_price', 'Relative Price', '%{y:.2f}')
                                )
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
                                dcc.Graph(
                                    id='trend_mc_relative', 
                                    config=graph_config,
                                    figure=generate_trend([], datetime.strftime(date.today()-timedelta(90), '%Y-%m-%d'), datetime.strftime(date.today(), '%Y-%m-%d'), 'relative_cap', 'Relative Market Cap', '%{y:.2f}')
                                )
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
            Input('market_filter2', 'value'),
            Input('rewards_filter2', 'value')])
@cache.memoize(timeout=20)
def update_filter_trend(gem_filter, tier_filter, sector_filter, market_filter, rewards_filter):
    if not gem_filter and not tier_filter and not sector_filter and not market_filter and not rewards_filter:
        filtered_json = json.dumps([]) # get_gem_list(master))
        return filtered_json
    else:
        filtered_gem_list = filter_gem_list(gem_filter, tier_filter, sector_filter, market_filter, rewards_filter)
        filtered_json = json.dumps(filtered_gem_list)
        return filtered_json


@app.callback(Output('trend_price', 'figure'),
	[Input('filter-trend', 'data'),
            Input('trend_date_picker', 'start_date'),
            Input('trend_date_picker', 'end_date')])
@cache.memoize(timeout=20)
def update_trend_price(filtered_json, start_date, end_date):
    filtered_gem_list = json.loads(filtered_json)
    return generate_trend(filtered_gem_list, start_date, end_date, 'relative_price', 'Relative Price', '%{y:.2f}')


@app.callback(Output('trend_market_cap', 'figure'),
	[Input('filter-trend', 'data'),
            Input('trend_date_picker', 'start_date'),
            Input('trend_date_picker', 'end_date')])
@cache.memoize(timeout=20)
def update_trend_market_cap(filtered_json, start_date, end_date):
    filtered_gem_list = json.loads(filtered_json)
    return generate_trend(filtered_gem_list, start_date, end_date, 'market_caps', 'Market Cap ($)', '$%{y:,.0f}')


@app.callback(Output('trend_mc_relative', 'figure'),
	[Input('filter-trend', 'data'),
            Input('trend_date_picker', 'start_date'),
            Input('trend_date_picker', 'end_date')])
@cache.memoize(timeout=20)
def update_trend_mc_relative(filtered_json, start_date, end_date):
    filtered_gem_list = json.loads(filtered_json)
    return generate_trend(filtered_gem_list, start_date, end_date, 'relative_cap', 'Relative Market Cap', '%{y:.2f}')


@app.callback(Output('trend_date_picker', 'initial_visible_month'),
	Input('trend_date_picker', 'end_date'),
            State('trend_date_picker', 'start_date'))
@cache.memoize(timeout=20)
def update_date_place(end_date, start_date):
    return datetime.strptime(start_date, '%Y-%m-%d')


