import os, sys
from datetime import datetime, timedelta, date
import json
import pandas as pd

import dash
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

pd.set_option('display.max_rows', 500)

graph_config = {
    'modeBarButtonsToRemove': [
        'pan2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'select2d', 'autoScale2d', 'resetScale2d',
        'hoverClosestCartesian','hoverCompareCartesian', 'toggleSpikelines', 'zoom2d',
        'sendDataToCloud', 'hoverClosestPie', 'toggleHover', 'resetViewMapbox'
    ],
    'displaylogo': False,
    'displayModeBar': True,
    'modeBarButtonsToAdd':['drawline', 'drawrect', 'eraseshape'],
    'toImageButtonOptions': {'height': None, 'width': None, 'scale': 20},
}


def generate_candle(df, var, candle, y_text, shape_data):
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
    fig.add_trace(go.Scatter(x=[min(df['timestamp']), max(df['timestamp'])+(max(df['timestamp'])-min(df['timestamp']))*0.1], 
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
        margin={'l': 0, 'r': 0, 't': 0, 'b': 0, 'pad': 0},
        xaxis=dict(
            gridcolor='rgba(176,179,184, 0.25)',
            gridwidth=1,
            title=dict(text=''),
            titlefont=dict(family='Supermolot', size=14, color=base_colours['primary_text']),
            tickfont=dict(family='Supermolot', size=12, color=base_colours['secondary_text']),
            #showgrid=False,
            range=[min(df['timestamp']), max(df['timestamp'])+(max(df['timestamp'])-min(df['timestamp']))*0.1]
        ),
        yaxis=dict(
            gridcolor='rgba(176,179,184, 0.5)',
            gridwidth=1,
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
        hoverlabel=dict(font=dict(family='Supermolot', color=base_colours['primary_text'])),
        hovermode='x unified',
        height=500,
        legend=dict(font=dict(family='Supermolot', color=base_colours['text'])),
        annotations=[dict(xref='paper', x=0.94, y=df[var].iloc[-1],
                                  xanchor='left', yanchor='middle',
                                  text=round(df[var].iloc[-1], 4),
                                  font=dict(family='Supermolot', color=base_colours['black'], size=12),
                                  bgcolor=price_color,
                                  showarrow=False,
        )],
        # style of new shapes
        dragmode='drawline',
        newshape=dict(line_color=base_colours['primary_text'],opacity=1, line=dict(width=2)),
        modebar=dict(orientation='v', activecolor=base_colours['primary_text']),
    )
    
    fig.update_xaxes(
        zerolinecolor=base_colours['sidebar'], 
        zerolinewidth=1, 
        rangeslider_visible=False, 
        showline=True, 
        linewidth=1, 
        linecolor='rgba(176,179,184, 0.25)', 
        mirror=True
    )
    fig.update_yaxes(zerolinecolor=base_colours['sidebar'], 
        zerolinewidth=1, 
        showline=True, 
        linewidth=1, 
        linecolor='rgba(176,179,184, 0.25)', 
        mirror=True
    )
    if shape_data:
        for shape in shape_data:
            fig.add_shape(
                editable=True,
                layer='above',
                type=shape['type'],
                x0=shape['x0'],
                x1=shape['x1'],
                y0=shape['y0'],
                y1=shape['y1'],
                line=dict(
                    color=base_colours['primary_text'],
                    width=2,
                )
            )
    return fig
  
  
def generate_table_data(df):
    df['timestamp'] = df.timestamp.dt.strftime('%Y-%m-%d %H:%M')
    return df.sort_index(ascending=False).to_dict('records')
 
    
def get_candle_options():
    options = []
    candle_list = ['15m', '30m', '1h', '2h', '4h', '12h', '1D', '3D', '1W']
    value_list = ['15Min', '30Min', '1h', '2h', '4h', '12h', '1D', '3D', '1W']
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
                                                ),
                                            ],
                                            sm=2,
                                            style={'padding-right': 10, 'padding-left': 10, 'padding-top': 20,'text-align': 'center'},
                                        ),
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        html.H4(id='uni_price'),
                                                    ],
                                                    id='uni_price_div',
                                                ),
                                            ],
                                            sm=4,
                                            style={'padding-right': 10, 'padding-left': 10, 'padding-top': 25, 'text-align': 'center'},
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
                                            sm=2,
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
                                                            value='4h',
                                                            style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            sm=2,
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
                                                            value=365,
                                                            style={'width': 'calc(100%-40px)', 'margin-bottom': 10},
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            sm=2,
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
                                    figure=generate_candle(get_uni_data('gmx', 7), 'usd_price', '1h', 'GMX/USD', []),
                                    style={'padding-top': 20},
                                )
                            ],
                            className="pretty_container",
                            style={'height': 'auto'},
                        ),
                    ],
                    xl=12,
                    style={'padding': 0}
                ),
            ],
        ),
	dbc.Row(
		dbc.Col(
			html.Div(
				[
					html.P('Uniswap Transactions', id='uni_table_tooltip', style={'text-align': 'center'}),
					dbc.Tooltip(
					    'Table can be sorted by column and filtered using the dropdowns',
					    target='uni_table_tooltip',
					    style={'font-family': 'Supermolot'}
					),
					dash_table.DataTable(
						id="uni_table",
						#sort_action='native',
						sort_by=[{'column_id': 'timestamp', 'direction': 'asc'}],
						style_table={'overflowY': 'auto', 'border': '{} {} {}'.format('1px', 'solid', base_colours['cg_border'])},
						fixed_rows={'headers': True},
						#style_as_list_view=True,
						columns=[
							{"name": ["Datetime"], "id": "timestamp", "type": "numeric"},
							{"name": ["Action"], "id": "action", "type": "text"},
							{"name": ["Price"], "id": "usd_price", "type": "numeric",
							 	"format": Format(
									precision=3,
									scheme=Scheme.fixed,
									symbol=Symbol.yes, 
									symbol_prefix='$'
								)
							},
							{"name": ["GMX"], "id": "n_GMX", "type": "numeric",
								"format": Format(
									precision=0,
									scheme=Scheme.fixed,
									group=Group.yes, 
									groups=3
								)
                                                        },
							{"name": ["ETH"], "id": "n_ETH", "type": "numeric",
								"format": Format(
									precision=2,
									scheme=Scheme.fixed,
								)
                                                        },
							{"name": ["USD"], "id": "nUSD", "type": "numeric",
							 	"format": Format(
									precision=3,
									scheme=Scheme.fixed,
									group=Group.yes, 
									groups=3,
									symbol=Symbol.yes, 
									symbol_prefix='$'
								)
							},
							{"name": ["Txn Hash"], "id": "tx_hash", "type": "text"},
                                                        # {"name": ["Arbiscan"], "id": "arbiscan", "type": "text", "presentation": "markdown"},
                                                        {"name": ["Address"], "id": "address", "type": "text"}# , "presentation": "markdown"},
						],
						#page_current=0,
						#page_size=PAGE_SIZE,
						page_action='none',
                                                virtualization=True,
						data=generate_table_data(get_uni_data('gmx', 7)),
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
							{'if': {'column_id': 'action'}, 'textAlign': 'left'},
							{'if': {'column_id': 'tx_hash'}, 'textAlign': 'left'},
							{'if': {'column_id': 'address'}, 'textAlign': 'left'},
							{'if': {'column_id': 'timestamp'}, 'textAlign': 'left'},
						],
						style_data_conditional=[
							#{'if': {'row_index': 'odd'},
							# 'backgroundColor': base_colours['card'],
							# 'color': base_colours['text']},
							#{'if': {'row_index': 'even'},
							# 'backgroundColor': base_colours['alt_row'],
							# 'color': base_colours['text']},
							{'if': {'column_id': 'timestamp'}, 'color': base_colours['text']},
							{'if': 
							    	{
							    		'filter_query': '{action} = BUY',
									'column_id': 'action'
								},
								'color': palette['green']['50']
							},
							{'if': 
								{
									'filter_query': '{action} = SELL',
									'column_id': 'action'
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
							{'if': {'column_id': 'action'}, 'textAlign': 'left'},
							{'if': {'column_id': 'tx_hash'}, 'textAlign': 'left'},
							{'if': {'column_id': 'address'}, 'textAlign': 'left'},
							{'if': {'column_id': 'timestamp'}, 'textAlign': 'left'},
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
    ],
    id='uniswap-container',
)


#@app.callback(Output('uni-data', 'data'),
#	[Input('chart-interval', 'n_intervals'),
#            Input('period_filter', 'value')],
#        prevent_initial_call=True)
#def update_uni_data(n_intervals, period):
#	df = get_uni_data('gmx', period)
#	return df.to_json()

'''
@app.callback(Output('uni_candlestick', 'extendData'),
	[Input('uni-data', 'data'),
	    Input('candle_filter', 'value')],
	[State('currency_filter', 'value')],
        prevent_initial_call=True)
def update_uni_trend_data(json_data, candle, currency):
    df = pd.read_json(json_data)
    data_vol = get_volume_data(df, candle)
    if currency == 'usd':
        data_ohlc = get_candle_data(df, 'usd_price', candle)
    elif currency == 'eth':
    	data_ohlc = get_candle_data(df, 'gmxeth', candle)
		
    if data_ohlc['close'].iloc[-1] >= data_ohlc['open'].iloc[-1]:
        price_color = palette['green']['50']
    elif data_ohlc['close'].iloc[-1] < data_ohlc['open'].iloc[-1]:
        price_color = palette['red']['50']
    else:
        price_color = color=base_colours['secondary_text']

    data_ohlc = data_ohlc.dropna()
    data_vol = data_vol.dropna()
	
    data = dict(
        x=[data_ohlc.index],
        open=[data_ohlc['open']],
        high=[data_ohlc['high']],
        low=[data_ohlc['low']],
        close=[data_ohlc['close']])

    return (data, [0])
'''
	
@app.callback(Output('uni_candlestick', 'figure'),
	[Input('currency_filter', 'value'),
            Input('chart-interval', 'n_intervals'),
	    Input('candle_filter', 'value'),
	    Input('period_filter', 'value'),
	    Input('gmx_shapes', 'data')],
        prevent_initial_call=True)
def update_uni_trend(currency, n_intervals, candle, interval, shape_data):
    df = get_uni_data('gmx', interval)
    if shape_data:
        shape_data = json.loads(shape_data)
    else:
        shape_data = []
    if currency == 'usd':
        return generate_candle(df, 'usd_price', candle, 'GMX/USD', shape_data)
    elif currency == 'eth':
        return generate_candle(df, 'gmxeth', candle, 'GMX/ETH', shape_data)


@app.callback(Output('gmx_shapes', 'data'),
    [Input('uni_candlestick', 'relayoutData')],
    State('gmx_shapes', 'data'),
    prevent_initial_call=True)
def on_gmx_annotation(relayout_data, shape_data):
    if relayout_data:
        if 'shapes' in relayout_data:
            return json.dumps(relayout_data["shapes"], indent=2)
        elif 'shapes' in list(relayout_data.keys())[0]:
            shape_data = json.loads(shape_data)
            idx = list(relayout_data.keys())[0][7:8]
            shape_data[int(idx)]['x0'] = relayout_data['shapes[{}].x0'.format(idx)]
            shape_data[int(idx)]['x1'] = relayout_data['shapes[{}].x1'.format(idx)]
            shape_data[int(idx)]['y0'] = relayout_data['shapes[{}].y0'.format(idx)]
            shape_data[int(idx)]['y1'] = relayout_data['shapes[{}].y1'.format(idx)]
            return json.dumps(shape_data, indent=2)
        else:
            return dash.no_update
    else:
        return dash.no_update


@app.callback(Output('uni_price', 'children'),
    [Input('chart-interval', 'n_intervals'),
        Input('currency_filter', 'value')],
    prevent_initial_call=True)
def update_uni_price(n_intervals, currency):
    df = get_uni_data('gmx', 1)
    if currency == 'usd':
        return '{} USD'.format(round(df['usd_price'].iloc[-1], 4))
    elif currency == 'eth':
        return '{} ETH'.format(round(df['gmxeth'].iloc[-1], 5))


@app.callback(Output('uni_table', 'data'),
    [Input('chart-interval', 'n_intervals'),
    Input('period_filter', 'value')],
    prevent_initial_call=True)
def update_table(n_intervals, interval):
    df = get_uni_data('gmx', interval)
    return generate_table_data(df)
        

