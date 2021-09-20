import os, sys
from datetime import datetime, timedelta, date
import json
import requests
import time

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
from plotly.subplots import make_subplots

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
    gem_style.append([item, None])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dash'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dot'])
for item in px.colors.qualitative.Pastel:
    gem_style.append([item, 'dashdot'])


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


GMX_contract = "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a"
sGMX_contract = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"
GMX_ETH_LP = '0x80a9ae39310abf666a87c743d6ebbd0e8c42158e'

API_key = "YWR5E9YUBPE2X6KNXG99D2MX1UHPYDFDBGT"


def get_all_tx():
    r_all = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&contractaddress={}&address={}&startblock=0&endblock=2500000&sort=asc&apikey={}'
                        .format(GMX_contract, sGMX_contract, API_key))

    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {
        'value': [],
        'cum_value': [],
        'timestamp': [],
        'in/out': []
    }

    for result in r_all.json()['result']:
        if result['to'] == '0x908c4d94d34924765f1edc22a1dd098397c59dd4':
            value = float(float(result['value'])*1e-18)
            in_out = 'IN'
        else:
            value = -float(float(result['value'])*1e-18)
            in_out = 'OUT'
        timestamp = result['timeStamp']
        
        cum_value = 0

        output_dict['value'].append(value)
        output_dict['cum_value'].append(cum_value)
        output_dict['timestamp'].append(timestamp)
        output_dict['in/out'].append(in_out)


    df = pd.DataFrame.from_dict(output_dict) 
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    
    for i, value in enumerate(df['value']):
        if i == 0:
            prev = 0
        else:
            prev = df['cum_value'].iloc[i-1]
        cum_value = prev + value
        df['cum_value'].iloc[i] = cum_value

        #print('idx={}, value={}, prev={}, cum_value={}'.format(i, value, prev, cum_value))

    df = df[~(df['timestamp'] < '2021-09-06 15:00:00')]
    df['Staked %'] = df['cum_value']/6490428*100
    return df


def get_all_LP_tx():
    r_all = []
    for i in range(5):
        start = 300000+i*300000
        end = 600000+i*300000
        r_page = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&address={}&startblock={}&endblock={}&sort=asc&apikey={}'
                            .format(GMX_ETH_LP, start, end, API_key))
        #print(r_page.json()['result'][0])
        r_all.extend(r_page.json()['result'])
        
    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {}
    
    for i, result in enumerate(r_all):
        try:
            tx = result['hash']
            timestamp = result['timeStamp']
            blocknumber = result['blockNumber']
            
            if tx in output_dict.keys():
                pass
            else:
                output_dict[tx] = {'timestamp': timestamp, 'blocknumber': blocknumber}


            if result['to'] == GMX_ETH_LP:
                in_out = 'in'
                
                if result['tokenName'] == 'GMX':
                    token = 'GMX'
                    amt = float(result['value'])*1e-18
                    output_dict[tx]['in amt'] = amt
                    output_dict[tx]['in token'] = token
                    
                elif result['tokenName'] == 'Wrapped Ether':
                    token = 'ETH'
                    amt = float(result['value'])*1e-18
                    output_dict[tx]['in amt'] = amt
                    output_dict[tx]['in token'] = token
            elif result['from'] == GMX_ETH_LP:
                in_out = 'out'
                
                if result['tokenName'] == 'GMX':
                    token = 'GMX'
                    amt = float(result['value'])*1e-18
                    output_dict[tx]['out amt'] = amt
                    output_dict[tx]['out token'] = token
                    
                elif result['tokenName'] == 'Wrapped Ether':
                    token = 'ETH'
                    amt = float(result['value'])*1e-18
                    output_dict[tx]['out amt'] = amt
                    output_dict[tx]['out token'] = token
        except Exception as e:
            print(e)
                    
    df = pd.DataFrame.from_dict(output_dict, orient='index')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    

    df = df[~(df['timestamp'] < '2021-09-06 15:00:00')]
        
    price_list = []
    
    for i, sell in enumerate(df['in token']):
        if sell == 'ETH':
            price = df['in amt'].iloc[i] / df['out amt'].iloc[i]
        elif sell == 'GMX':
            price = df['out amt'].iloc[i] / df['in amt'].iloc[i]
        price_list.append(price)
    
    df['price'] = price_list
    
    return df.set_index('timestamp')


def generate_staked_trend(df, dff, y_var, y_text, hover_temp):
    fig_range = make_subplots(specs=[[{"secondary_y": True}]])
    fig_range.add_trace(
        go.Scatter(
            x=df.index, 
            y=df['price'], 
            name='GMX/ETH Price', 
            hovertemplate='%{y:,.5f}',
            line=dict(color=base_colours['tf_accent3']),
            textfont=dict(family='Supermolot', color=base_colours['text'], size=13),
        ),
        secondary_y=False
    )
    fig_range.add_trace(
        go.Scatter(
            x=dff['timestamp'], 
            y=dff[y_var], 
            name='Total Staked', 
            hovertemplate=hover_temp,
            line=dict(color=base_colours['tf_accent']),
            textfont=dict(family='Supermolot', color=base_colours['text'], size=13),
            customdata=round(dff[y_var]/6490429*100, 2)
        ),
        secondary_y=True
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
            title=dict(text='GMX/ETH'),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            ticksuffix='   ',
            tickprefix='',
#            dtick=round(max(df['price']), 3)/5
            #range=[min(df['price']), max(df['price'])]

        ),
        yaxis2=dict(
            #gridcolor=base_colours['secondary_text'],
            showgrid=False,
            title=dict(text=y_text),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            ticksuffix='   ',
            tickprefix='',
#            dtick=round(max(dff[y_var])-min(dff[y_var]), -5)/5
#            scaleanchor='y1',
            #range=[min(dff[y_var]), max(dff[y_var])]
        ),
        showlegend=False,
        font={'color': base_colours['primary_text']},
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['black'])),
        hovermode='x',
        height=650,
        legend=dict(font=dict(family='Supermolot', color=base_colours['text']))
    )

    fig_range.update_xaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1) #, rangeslider_visible=True)

    return fig_range




layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.P('Historical View of GMX Price and Total Staked Supply', id='sGMX_trend_tip', style={'text-align': 'center'}),
                                dcc.Graph(
                                    id='trend_sGMX',
                                    config=graph_config,
                                    figure=generate_staked_trend(get_all_LP_tx(), get_all_tx(),'cum_value', 'Staked GMX Count', '%{y:,.0f} (%{customdata}%)')
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
    id='staking-container',
)


@app.callback(Output('trend_sGMX', 'figure'),
	[Input('live-interval', 'n_intervals')])
def update_trend_price(n_intervals):
    return generate_staked_trend(get_all_LP_tx(), get_all_tx(), 'cum_value', 'Staked GMX Count', '%{y:,.0f} <b>(%{customdata}%)</b>')


