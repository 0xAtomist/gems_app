import requests
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import redis
import pyarrow as pa

from auth import auth_conf

GMX_contract = "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a"
sGMX_contract = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"

GMX_ETH_LP = '0x80a9ae39310abf666a87c743d6ebbd0e8c42158e'
ETH_USDC_LP = '0x17c14d2c404d167802b16c450d3c99f88f2c4f4d'

API_key = auth_conf['arbiscan']['API_KEY']

pd.set_option('display.max_rows', 1000)


def get_recent_LP_tx(LP_contract, top_pair, bottom_pair, decimal_ratio, offset):
    r_all = []
    r_100 = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&address={}&page=1&offset={}&sort=desc&apikey={}'
                        .format(LP_contract, offset, API_key))
    
    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {}

    # print(len(r_100.json()['result']))

    for i, result in enumerate(r_100.json()['result']):
        try:
            # present in every tx
            tx = result['hash']
            timestamp = result['timeStamp']
            blocknumber = result['blockNumber']
            
            if tx in output_dict.keys(): # check if already processed
                pass
            else:
                output_dict[tx] = {'timestamp': timestamp, 'blocknumber': blocknumber, 'tx_hash': tx}

            if result['to'] == LP_contract: #sendingn to Uni LP
                amt = float(result['value'])*1e-18
                output_dict[tx]['in amt'] = amt
                    
                if result['tokenSymbol'] == top_pair: #GMX being sent to LP (SELL)
                    token = top_pair
                    output_dict[tx]['in token'] = token
                    output_dict[tx]['address'] = result['from']

                    
                elif result['tokenSymbol'] == bottom_pair: #WETH being sent to LP (BUY)
                    token = bottom_pair
                    output_dict[tx]['in token'] = token

                    
            elif result['from'] == LP_contract: #receiving from Uni LP
                amt = float(result['value'])*1e-18
                output_dict[tx]['out amt'] = amt
                
                if result['tokenSymbol'] == top_pair: #GMX being received from LP (BUY)
                    token = top_pair
                    output_dict[tx]['out token'] = token
                    output_dict[tx]['address'] = result['to']

                    
                elif result['tokenSymbol'] == bottom_pair: #WETH being received from LP (SELL)
                    token = bottom_pair
                    output_dict[tx]['out token'] = token
                    
        except Exception as e:
            print(e)
                    
    df = pd.DataFrame.from_dict(output_dict, orient='index')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    # print(df)

    df = df[~(df['timestamp'] < '2021-09-06')]
    df = df.dropna()
    df = df[df['address'] != '0x7Ee730a0438529F1D5FeD33c27457D1EACEc402E'.lower()]
    df = df[df['address'] != '0xfeb6d3004b9cf7595af96dba23d9ec8e5f6e3ebc'.lower()]
    print(df)
    price_list = []
        
    for i, sell in enumerate(df['in token']):
        if sell == bottom_pair:
            price = df['in amt'].iloc[i] / df['out amt'].iloc[i]
        elif sell == top_pair:
            price = df['out amt'].iloc[i] / df['in amt'].iloc[i]
        price_list.append(price*decimal_ratio)
    
    df['price'] = price_list
    dt = pd.to_datetime(df['timestamp'], format='%Y/%m/%d %H:%M:%S')
    delta = pd.to_timedelta(df.groupby(dt).cumcount(), unit='ms')
    df['timestamp'] = dt + delta.values
    df = df.dropna().set_index('timestamp', drop=False)
    df = df.sort_index()
    #new_idx = range(len(df))
    #df = df.set_index(pd.Index(new_idx), drop=False)
    #print(df)
    # df = df.dropna().drop_duplicates(subset=['timestamp']).set_index('timestamp', drop=False)
    # df = df.dropna()

    return df


def get_new_eth_price(ethusd_price, df_bottom, idx):
    for i in range(10):
        if ethusd_price > 100000:
            print(df_bottom['price'].iloc[idx-(i+1)])
            ethusd_price = df_bottom['price'].iloc[idx-(i+1)]
        else:
            return ethusd_price


def get_usd_dataset(df_top, df_bottom):
    usd_list = []
    eth_list = []
    vol_list = []
    n_GMX_list = []
    n_ETH_list = []
    n_USD_list = []
    action_list = []

    for i, dt in enumerate(df_top.index):
        idx = df_bottom.index.get_loc(dt, method='nearest')
        ethusd_price = df_bottom['price'].iloc[idx]
        ethusd_price = get_new_eth_price(ethusd_price, df_bottom, idx)
        gmxusd_price = df_top['price'].iloc[i] * ethusd_price
        usd_list.append(gmxusd_price)
        eth_list.append(ethusd_price)

        if df_top['in token'].iloc[i] == 'GMX':
            n_GMX = df_top['in amt'].iloc[i]
            n_ETH = df_top['in amt'].iloc[i] * gmxusd_price/ethusd_price
            n_USD = df_top['in amt'].iloc[i] * gmxusd_price
            vol = df_top['in amt'].iloc[i] * gmxusd_price
            action = 'SELL'
        elif df_top['in token'].iloc[i] == 'WETH':
            n_GMX = df_top['in amt'].iloc[i] * ethusd_price/gmxusd_price
            n_ETH = df_top['in amt'].iloc[i]
            n_USD = df_top['in amt'].iloc[i] * ethusd_price
            vol = df_top['in amt'].iloc[i] * ethusd_price
            action = 'BUY'
        n_GMX_list.append(n_GMX)
        n_ETH_list.append(n_ETH)
        n_USD_list.append(n_USD)
        vol_list.append(vol)
        action_list.append(action)

    df_top['usd_price'] = usd_list
    df_top['eth_price'] = eth_list
    df_top['n_GMX'] = n_GMX_list
    df_top['n_ETH'] = n_ETH_list
    df_top['nUSD'] = n_USD_list
    df_top['volume'] = vol_list
    df_top['action'] = action_list
    df_top['gmxeth'] = df_top['usd_price']/df_top['eth_price']

    df_top = df_top.drop_duplicates(subset=['tx_hash'])
    return df_top


r = redis.StrictRedis('localhost')
context = pa.default_serialization_context()


while True:
    # get recent txns
    try:
        df_100 = get_usd_dataset(get_recent_LP_tx(GMX_ETH_LP, 'GMX', 'WETH', 1, 200),
                                 get_recent_LP_tx(ETH_USDC_LP, 'WETH', 'USDC', 1e12, 1000))
        #print(df_100)
        
        for i, timestamp in enumerate(df_100.index):
            df_all = context.deserialize(r.get('gmx-uniswap'))
            if timestamp in df_all.index:
                #print('already stored')
                pass
            else:
                print('requires storing')
                df_all = df_all.append(df_100.iloc[i])
            r.set('gmx-uniswap', context.serialize(df_all).to_buffer().to_pybytes())
    except Exception as e:
        print(e)
    time.sleep(10)

