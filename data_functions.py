from __future__ import division
import os, sys
import math
import time
import json
from datetime import timedelta, date, datetime

import pyarrow as pa
import pandas as pd
from pandas.tseries.offsets import *
import redis
import numpy as np
import hmac
import requests
from pycoingecko import CoinGeckoAPI
from app import cache

#from flask_login import current_user
#import smtplib
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
#from email.mime.image import MIMEImage
#from PIL import Image

#from app.auth import auth_conf


# path to this script
script_dir = os.path.dirname(__file__)

#@cache.memoize(timeout=20)
def get_gem_list(master):  # get list of site IDs publishing data
    gem_list = list(master["gems"].keys())
    gem_list.remove('usd-coin')
    return gem_list

#@cache.memoize(timeout=0)
def get_gem_info():  # load JSON storing client site information
    rel_path_pub = 'master.json'
    abs_path_pub = os.path.join(script_dir, rel_path_pub)
    with open(abs_path_pub, 'r') as f:
        master = json.load(f)
    return master


@cache.memoize(timeout=20)
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
		if i == 6:
			break

	dff = pd.DataFrame(market_list)
	return df, dff


@cache.memoize(timeout=20)
def get_gem_inspection(gem):
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('{}-inspect'.format(gem)))
    return df


@cache.memoize(timeout=20)
def get_gem_markets(gem):
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('{}-markets'.format(gem)))
    return df


@cache.memoize(timeout=20)
def get_chart_range_data(gem, start_date, end_date):
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('{}-trending'.format(gem)))
    
    dff = df[(df['Datetime'] > start_date) & (df['Datetime'] < end_date)]
    dff = dff.reset_index()
    dff['relative_price'] = dff['price']/dff['price'].iloc[0]
    dff['relative_cap'] = dff['market_caps']/dff['market_caps'].iloc[0]
    return dff


@cache.memoize(timeout=20)
def get_chart_period_data(gem, period):
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('{}-{}d-chart'.format(gem, period)))
    return df


@cache.memoize(timeout=20)
def get_btc_daily():
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('btc_history'))
    return df


@cache.memoize(timeout=20)
def get_data_recent(gem):  # get most recent reading for site input
    r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)
    output = r.hgetall(gem)

    df = pd.DataFrame.from_dict(output, orient='index').T
    num_cols = df.columns.drop(['symbol', 'ath_date', 'name', 'last_updated', 'atl_date', 'image'])
    df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')

    #print(df['current_price'][0])
    #print(df.loc[0]['symbol'], df.loc[0]['last_updated'])

    return df.loc[0]


@cache.memoize(timeout=20)
def get_extended_data(gem):
    master = get_gem_info()
    tweet_price = master['gems'][gem]['Tweet Price']
    tweet_date = master['gems'][gem]['Tweet Date']

    df = get_data_recent(gem)
    df_btc = get_btc_daily()

    btc_now = get_data_recent('bitcoin')['current_price']
    gem_now = df['current_price']
    tweet_time = datetime.timestamp(datetime.strptime(tweet_date, '%Y-%m-%d'))
    btc_tweet = df_btc.loc[df_btc['time'] == tweet_time]['close'].values[0]
    df['btc_usd_x'] = btc_now/btc_tweet
    gem_tweet = float(tweet_price)

    df['fdv_tot'] = df['current_price'] * df['total_supply']
    df['mc_fdv_ratio'] = df['market_cap'] / df['fdv_tot']
    df['gem_usd_x'] = df['current_price'] / tweet_price - 1
    df['gem_btc_x'] = (gem_now/btc_now) / (gem_tweet/btc_tweet) - 1
    if datetime.timestamp(datetime.strptime(df['ath_date'], '%Y-%m-%dT%H:%M:%S.%fZ')) < tweet_time:
        df_trend = get_chart_range_data(gem, tweet_date, datetime.today().strftime('%Y-%m-%d'))
        ath_post_idx = df_trend['price'].idxmax()
        ath_post = df_trend['price'].iloc[ath_post_idx]
        df['ath_gem_usd_x'] = ath_post / gem_tweet - 1
        df['ath_gem_btc_x'] = (ath_post/btc_now) / (gem_tweet/btc_tweet) - 1
    else:
        df['ath_gem_usd_x'] = df['ath'] / gem_tweet - 1
        df['ath_gem_btc_x'] = (df['ath']/btc_now) / (gem_tweet/btc_tweet) - 1
    df['20x']  = tweet_price * 20
    df['50x'] = tweet_price * 50

    return df


@cache.memoize(timeout=20)
def get_filtered_df(filtered_gem_list):
    #print(filtered_gem_list)
    if filtered_gem_list:
        dfs = []
        for gem in filtered_gem_list:

            s = get_extended_data(gem)
            df = pd.DataFrame(s).transpose()
            df['id'] = gem
            df = df.set_index('id')
            dfs.append(df)
        df_master = pd.concat(dfs)
        df_master.rename(columns={
            'price_change_percentage_1h_in_currency': '1h_col',
            'price_change_percentage_24h_in_currency': '24h_col',
            'price_change_percentage_7d_in_currency': '7d_col'
        }, inplace=True)
        #print(df_master)
        return df_master
    else:
        return pd.DataFrame()


@cache.memoize(timeout=20)
def get_uni_data(gem, period):
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('{}-uniswap'.format(gem)))
    start_date = datetime.today() - timedelta(days=int(period))
    df = df[~(df['timestamp'] < start_date)].copy()
    return df


@cache.memoize(timeout=20)
def get_candle_data(df, var, candle):
    df_candle = df[var].resample(candle).ohlc()
    return df_candle


@cache.memoize(timeout=20)
def get_volume_data(df, candle):
    df_vol = df['volume'].resample(candle).sum()
    return df_vol


@cache.memoize(timeout=20)
def get_staked_data(gem):
    r = redis.StrictRedis('localhost')
    context = pa.default_serialization_context()
    df = context.deserialize(r.get('{}-staked'.format(gem)))
    return df


@cache.memoize(timeout=20)
def get_n_total(gem):
    r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)

    n_total = float(r.get('n-{}-total'.format(gem)))
    return n_total


@cache.memoize(timeout=20)
def get_n_staked(gem):
    r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)

    n_staked = float(r.get('n-{}-staked'.format(gem)))
    return n_staked


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


