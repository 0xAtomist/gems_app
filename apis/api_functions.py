from __future__ import division
import os, sys
import math
import time
import json
from datetime import timedelta, date, datetime

import pandas as pd
from pandas.tseries.offsets import *
#import redis
import numpy as np
import hmac
import requests
from pycoingecko import CoinGeckoAPI


# path to this script
script_dir = os.path.dirname(__file__)


def get_gem_list(master):  # get list of site IDs publishing data
    gem_list = list(master["gems"].keys())
    return gem_list


def get_gem_info():  # load JSON storing client site information
    rel_path_pub = '../master.json'
    abs_path_pub = os.path.join(script_dir, rel_path_pub)
    with open(abs_path_pub, 'r') as f:
        master = json.load(f)
    return master


def get_api_inspections(gem):
    cg = CoinGeckoAPI()

    token_data = cg.get_coin_by_id(gem)

    token_dict = {
        'id': gem,
        'categories': token_data['categories'],
        'description': token_data['description']['en'],
        'platforms': list(token_data['platforms'].keys()),
        'contracts': list(token_data['platforms'].values()),
        'website': token_data['links']['homepage'][0],
        'explorer': token_data['links']['blockchain_site'][0],
        'chat': token_data['links']['chat_url'],
        'annoucement': token_data['links']['announcement_url'],
        'twitter': 'https://twitter.com/{}'.format(token_data['links']['twitter_screen_name']),
        'rank': token_data['market_cap_rank'],
        'liq_score': token_data['liquidity_score'],
        'comm_score': token_data['community_score'],
        'tvl': token_data['market_data']['total_value_locked'],
        'volume': token_data['market_data']['total_volume']['usd'],
        'market_cap': token_data['market_data']['market_cap']['usd'],
        '24h': token_data['market_data']['price_change_percentage_24h']/100,
        '7d': token_data['market_data']['price_change_percentage_7d']/100,
        '14d': token_data['market_data']['price_change_percentage_14d']/100,
        '30d': token_data['market_data']['price_change_percentage_30d']/100,
        '60d': token_data['market_data']['price_change_percentage_60d']/100,
        '200d': token_data['market_data']['price_change_percentage_200d']/100,
        '1y': token_data['market_data']['price_change_percentage_1y']/100
    }
    
    df = pd.Series(token_dict)
    
    market_list = []

    for i, market in enumerate(token_data['tickers']):
        market_dict = {
            'target': market['target'],
            'name': market['market']['name'],
            'price': market['converted_last']['usd'],
            'volume': market['converted_volume']['usd'],
            'volume_percent': market['converted_volume']['usd']/token_dict['volume'],
            'trust': market['trust_score'],
            'spread': market['bid_ask_spread_percentage'],
            'last_traded': market['last_traded_at'],
            'trade_url': market['trade_url'],
        }
        market_list.append(market_dict)
        if i == 9:
            break

    dff = pd.DataFrame(market_list)

    return df, dff


def get_chart_data(gem, period):
    cg = CoinGeckoAPI()
    chart_data = cg.get_coin_market_chart_by_id(gem, 'usd', period)
    df_p = pd.DataFrame(chart_data['prices'], columns=['unix_time', 'price'])
    df_p['Datetime'] = pd.to_datetime(df_p['unix_time']/1000, unit='s')
    df_m = pd.DataFrame(chart_data['market_caps'], columns=['unix_time', 'market_caps'])
    df_m['Datetime'] = pd.to_datetime(df_m['unix_time']/1000, unit='s')
    df_p['market_caps'] = df_m['market_caps']
    return df_p


def get_api_markets():
    cg = CoinGeckoAPI()
    master = get_gem_info()

    markets_list = get_gem_list(master)
    extra_coins = ['bitcoin', 'ethereum', 'binancecoin']
    for extra in extra_coins:
        markets_list.append(extra)

    gem_markets = cg.get_coins_markets(
        ids=markets_list,
        vs_currency='usd',
        price_change_percentage='1h,24h,7d',
        sparkline='true'
    )

    df = pd.DataFrame(gem_markets)


    df = df.set_index('id')
    # Finalise df
    df = df.fillna(0)
    df['symbol'] = df['symbol'].str.upper()
    #print(df['sparkline_in_7d'])
    df = df.drop('sparkline_in_7d', axis=1)

    return df


def get_btc_history():
	r = requests.get('https://ftx.com/api/markets/BTC-PERP/candles?resolution=86400')

	btc_history = r.json()['result']

	df_btc = pd.DataFrame.from_dict(btc_history)
	df_btc['time'] = df_btc['time']/1000

	return df_btc


def get_data_recent(gem):  # get most recent reading for site input
	master = get_gem_info()
	tweet_price = master['gems'][gem]['Tweet Price']
	tweet_date = master['gems'][gem]['Tweet Date']
	tweet_price = master['gems'][gem]['Tweet Price']

	df = get_api_markets()

	return df.loc[gem]


def get_extended_data(gem):
	master = get_gem_info()
	tweet_price = master['gems'][gem]['Tweet Price']
	tweet_date = master['gems'][gem]['Tweet Date']
	tweet_price = master['gems'][gem]['Tweet Price']

	df = get_data_recent(gem)
	df_btc = get_btc_history()

	btc_now = get_api_markets().loc['bitcoin']['current_price']
	gem_now = df['current_price']
	tweet_time = datetime.timestamp(datetime.strptime(tweet_date, '%Y-%m-%d'))
	btc_tweet = df_btc.loc[df_btc['time'] == tweet_time]['close'].values[0]
	gem_tweet = tweet_price
	
	df['fdv_tot'] = df['current_price'] * df['total_supply']
	df['mc_fdv_ratio'] = df['market_cap'] / df['fdv_tot']
	df['gem_btc_x'] = df['current_price'] / tweet_price - 1
	df['btc_usd_x'] = btc_now/btc_tweet
	df['gem_btc_x'] = (gem_now/btc_now) / (gem_tweet/btc_tweet) - 1
	df['20x']  = tweet_price * 20
	df['50x'] = tweet_price * 50

	return df



def get_slider(gem):  # get settings for date range slider
    today = pd.Timestamp.today()
    tweet_date = get_gem_info()['gems'][gem]['Tweet Date']  # get product start date from publishers.json
    day_marks = (today - datetime.strptime(tweet_date, '%Y-%m-%d')).days  # number of days available on the slider
    month_marks = math.ceil(day_marks / 30)  # number of marks on slider (1 per month)
    m1date = today + DateOffset(days=-(day_marks + 1))  # first date on the slider
    datelist = pd.date_range(m1date, periods=month_marks, freq='M') + DateOffset(
        days=1)  # list of dates shown as monthly marks

    if today - m1date > pd.Timedelta('365 days'):
        month_marks = month_marks / 2 # 1 per 2 month
        datelist = pd.date_range(m1date, periods=month_marks, freq='2M') + DateOffset(
            days=1)  # list of dates shown as monthly marks

    dlist = pd.DatetimeIndex(datelist).normalize()
    timelist = (dlist.astype(
        np.int64) / 10 ** 9).values  # converted dates to unix timestamps (values for slider position)
    tags = {}
    for i, item in enumerate(dlist):
        tags[int(timelist[i])] = (item).strftime('%b-%y')  # tags on slider taken in format {value: label}
    return timelist[0], tags  # return first value on slider and tag dict


