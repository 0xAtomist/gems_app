from __future__ import division
import os, sys
import math
import time
import json
from datetime import timedelta, date, datetime

import pandas as pd
from pandas.tseries.offsets import *
import redis
import numpy as np
import hmac
import requests
from pycoingecko import CoinGeckoAPI

#from flask_login import current_user
#import smtplib
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
#from email.mime.image import MIMEImage
#from PIL import Image

from app.auth import auth_conf


# path to this script
script_dir = os.path.dirname(__file__)


def get_gem_list(master):  # get list of site IDs publishing data
	gem_list = list(master["gems"].keys())
	return gem_list


def get_gem_info():  # load JSON storing client site information
    rel_path_pub = '../../master.json'
    abs_path_pub = os.path.join(script_dir, rel_path_pub)
    with open(abs_path_pub, 'r') as f:
        master = json.load(f)
    return master


'''
def get_data_month(pub, start_date, end_date):  # get data for date range inputs


def get_data_real(pub):  # get most recent reading for site input
'''


def get_api_markets():
	cg = CoinGeckoAPI()
	master = get_gem_info()
	gem_list = get_gem_list(master)

	GEM_dict = dict.fromkeys(gem_list, [])

	markets_list = gem_list
	markets_list.append('bitcoin')

	gem_markets = cg.get_coins_markets(
		ids=markets_list,
		vs_currency='usd',
		price_change_percentage='1h,24h,7d',
		sparkline='true'
	)

	df = pd.DataFrame(gem_markets)

	df_gems = df.set_index('id')
	# Finalise df
	df_gems = df_gems.fillna(0)
	df_gems['symbol'] = df_gems['symbol'].str.upper()
	df = df_gems.drop('sparkline_in_7d', axis=1)

	return df


def get_btc_history():
	r = requests.get('https://ftx.com/api/markets/BTC-PERP/candles?resolution=86400')

	btc_history = r.json()['result']

	df_btc = pd.DataFrame.from_dict(btc_history)
	df_btc['time'] = df_btc['time']/1000

	return df_btc


def get_data_recent(gem):  # get most recent reading for site input
	r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)
	output = r.hgetall(gem)

	df = pd.DataFrame.from_dict(output, orient='index').T
	cols = df.columns.drop(['symbol', 'ath_date', 'name', 'last_updated', 'atl_date', 'image'])
	df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

	#print(df['current_price'][0])
	#print(df.loc[0]['symbol'], df.loc[0]['last_updated'])

	return df.loc[0]


def get_extended_data(gem):
	master = get_gem_info()
	tweet_price = master['gems'][gem]['Tweet Price']
	tweet_date = master['gems'][gem]['Tweet Date']
	tweet_price = master['gems'][gem]['Tweet Price']

	df = get_data_recent(gem)
	df_btc = get_btc_history()

	btc_now = get_data_recent('bitcoin')['current_price']
	gem_now = df['current_price']
	tweet_time = datetime.timestamp(datetime.strptime(tweet_date, '%Y-%m-%d'))
	btc_tweet = df_btc.loc[df_btc['time'] == tweet_time]['close'].values[0]
	gem_tweet = tweet_price
	
	df['fdv_tot'] = df['current_price'] * df['total_supply']
	df['mc_fdv_ratio'] = df['market_cap'] / df['fdv_tot']
	df['gem_usd_x'] = df['current_price'] / tweet_price - 1
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


