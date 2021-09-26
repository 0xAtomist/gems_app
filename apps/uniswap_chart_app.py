import os, sys
from datetime import datetime, timedelta, date
import json
import pandas as pd

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

from app import app, cache
from colours import *
from data_functions import get_uni_data, get_candle_data, get_volume_data


graph_config = {
    'modeBarButtonsToRemove': [
        'pan2d', 'lasso2d', 'select2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
        'hoverClosestCartesian','hoverCompareCartesian', 'toggleSpikelines', 'zoom2d',
        'sendDataToCloud', 'hoverClosestPie', 'toggleHover', 'resetViewMapbox'
    ],
    'displaylogo': False,
    'displayModeBar': False,
}


def generate_candle(df, var, candle, y_text):
    data_ohlc = get_candle_data(df, var, candle)
    data_vol = get_volume_data(df, candle)
    if data_ohlc['close'].iloc[-1] >= data_ohlc['open'].iloc[-1]:
        price_color = palette['green']['50']
    elif data_ohlc['close'].iloc[-1] < data_ohlc['open'].iloc[-1]:
        price_color = palette['red']['50']
    else:
        price_color = color=base_colours['secondary_text']

    data_ohlc = data_ohlc.dropna()
    data_vol = data_vol.dropna()
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Candlestick(x=data_ohlc.index,
                    open=data_ohlc['open'],
                    high=data_ohlc['high'],
                    low=data_ohlc['low'],
                    close=data_ohlc['close'],
                    increasing_line_color= palette['green']['50'],
                    decreasing_line_color = palette['red']['50'],
                    increasing_fillcolor= palette['green']['50'],
                    decreasing_fillcolor = palette['red']['50'],
                    name='{} Price'.format(y_text)
    ))
    fig.add_trace(go.Bar(x=data_vol.index, y=data_vol, marker={'color': '#30D5C8'}, name='USD Volume') , secondary_y=True)
    fig.add_trace(go.Scatter(x=[min(df.index), max(df.index)], 
                            y=[df[var].iloc[-1], df[var].iloc[-1]], 
                            mode='lines', 
                            line=dict(color=price_color, width=1, dash='dot'),
                            hoverinfo='skip',
    ))

    fig.update_xaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_yaxes(showspikes=True, spikecolor="grey", spikethickness=2, spikesnap="cursor", spikemode="across")
    fig.update_layout(spikedistance=-1, hoverdistance=100, hovermode='x')
    fig.update_layout(
        plot_bgcolor='#434343',
        paper_bgcolor=base_colours['card'],
        margin={'l': 0, 'r': 10, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            title=dict(text=''),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            showgrid=False,
            # range=[min(df.index), max(df.index)+(max(df.index)-min(df.index))*0.1]
        ),
        yaxis=dict(
            gridcolor=base_colours['secondary_text'],
            title=dict(text=y_text),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            ticksuffix='   ',
            tickprefix='',
            range=[min(df[var])*0.75, max(df[var])*1.05]
        ),
        yaxis2=dict(
            showgrid=False,
            #title=dict(text='USD Volume'),
            #titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            #tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            #ticksuffix='   ',
            #tickprefix='',
            range=[0, max(data_vol)*6],
            showticklabels=False
        ),
        showlegend=False,
        font={'color': base_colours['primary_text']},
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['black'])),
        hovermode='x',
        height=550,
        legend=dict(font=dict(family='Supermolot', color=base_colours['text'])),
        annotations=[dict(xref='paper', x=0.95, y=df[var].iloc[-1],
                                  xanchor='left', yanchor='middle',
                                  text=round(df[var].iloc[-1], 4),
                                  font=dict(family='Supermolot', color=base_colours['black'], size=12),
                                  bgcolor=price_color,
                                  showarrow=False,
        )]
    )

    fig.update_xaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1, rangeslider_visible=False)
    fig.update_yaxes(zerolinecolor=base_colours['sidebar'], zerolinewidth=1)
    return fig
  
  
def generate_table_data(df):
    return df.to_dict('records')
 
    
def get_candle_options():
    options = []
    candle_list = ['15m', '30m', '1h', '4h', '1D', '3D', '1W']
    value_list = ['15Min', '30Min', '1h', '4h', '1D', '3D', '1W']
    df = pd.DataFrame(data={'candle': candle_list, 'value': value_list})
    for i in df.index:
            options.append({'label': df.loc[i]['candle'], 'value': df.loc[i]['value']})
    return options


def get_period_options():
    options = []
    period_list = ['24h', '2d', '7d', '14d', '30d', '90d', '180d', '1y']
    value_list = [1, 2, 7, 14, 30, 90, 180, 365]
    df = pd.DataFrame(data={'period': period_list, 'value': value_list})
    for i in df.index:
            options.append({'label': df.loc[i]['period'], 'value': df.loc[i]['value']})
    return options


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
                                                        html.H2('GMX'),
                                                    ],
                                                    id='uni_name_div',
                                                    style={'vertical-align': 'middle'},
                                                ),
                                            ],
                                            md=3,
                                            style={'padding-right': 10, 'padding-left': 30, 'vertical-align': 'middle', 'padding-top': 20},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.H2(id='uni_price'),
                                                    ],
                                                    id='uni_price_div',
                                                ),
                                            ],
                                            md=3,
                                            style={'padding-right': 10, 'padding-left': 10, 'vertical-align': 'middle', 'padding-top': 20},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.P("Pair", style={'margin-bottom': 2}),
                                                        dcc.Dropdown(
                                                            id='currency_filter',
                                                            options=[{'label': 'USD', 'value': 'usd'}, {'label': 'ETH', 'value': 'eth'}],
                                                            multi=False,
                                                            value='usd',
                                                            style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            md=2,
                                            style={'padding-right': 10, 'padding-left': 10},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.P("Candle", style={'margin-bottom': 2}),
                                                        dcc.Dropdown(
                                                            id='candle_filter',
                                                            options=get_candle_options(),
                                                            multi=False,
                                                            value='1h',
                                                            style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            md=2,
                                            style={'padding-right': 10, 'padding-left': 10},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.P("Interval", style={'margin-bottom': 2}),
                                                        dcc.Dropdown(
                                                            id='period_filter',
                                                            options=get_period_options(),
                                                            multi=False,
                                                            value=7,
                                                            style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            md=2,
                                            style={'padding-right': 10, 'padding-left': 10},
                                        ),
                                    ],
                                    style={'padding-right': 10, 'padding-left': 10},
                                ),
                            ],
                            id='uni_ribbon',
                            className="pretty_container",
                            style={'height': 'auto', 'min-height': 50, 'padding': 10},
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
                                html.P('Uniswap Historical Price Data', id='uni_trend_tip', style={'text-align': 'center'}),
                                dbc.Tooltip(
                                    'Candle intervals and overall time period selectable above',
                                    target='uni_trend_tip',
                                    style={'font-family': 'Supermolot'}
                                ),
                                dcc.Graph(
                                    id='uni_candlestick',
                                    config=graph_config,
                                    figure=generate_candle(get_uni_data('gmx', 7), 'usd_price', '1h', 'GMX/USD')
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
    id='uniswap-container',
)

        
@app.callback(Output('uni_candlestick', 'figure'),
	[Input('chart-interval', 'n_intervals'),
            Input('candle_filter', 'value'),
            Input('period_filter', 'value'),
            Input('currency_filter', 'value')])
def update_uni_trend(n_intervals, interval, period, currency):
    if currency == 'usd':
        return generate_candle(get_uni_data('gmx', period), 'usd_price', interval, 'GMX/USD')
    elif currency == 'eth':
        return generate_candle(get_uni_data('gmx', period), 'gmxeth', interval, 'GMX/ETH')

 
@app.callback(Output('uni_price', 'children'),
	[Input('chart-interval', 'n_intervals'),
            Input('currency_filter', 'value')])
def update_uni_price(n_intervals, currency):
    df = get_uni_data('gmx', 1)
    print(df)
    if currency == 'usd':
        return '{} USD'.format(round(df['usd_price'].iloc[-1], 2))
    elif currency == 'eth':
        return '{} ETH'.format(round(df['gmxeth'].iloc[-1], 5))

       
        
