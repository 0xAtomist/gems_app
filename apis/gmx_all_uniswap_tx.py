import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import redis
import pyarrow as pa


GMX_contract = "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a"
sGMX_contract = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"

GMX_ETH_LP = '0x80a9ae39310abf666a87c743d6ebbd0e8c42158e'
ETH_USDC_LP = '0x17c14d2c404d167802b16c450d3c99f88f2c4f4d'

API_key = "YWR5E9YUBPE2X6KNXG99D2MX1UHPYDFDBGT"


def get_all_LP_tx(LP_contract, top_pair, bottom_pair, decimal_ratio, blocklength, iterations):
    r_all = []
    for i in range(iterations):
        start = 300000+i*blocklength-1
        end = 300000+blocklength+i*blocklength+1
        r_page = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&address={}&startblock={}&endblock={}&sort=asc&apikey={}'
                            .format(LP_contract, start, end, API_key))
        print(top_pair, i, len(r_page.json()['result']))
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
                output_dict[tx] = {'timestamp': timestamp, 'blocknumber': blocknumber, 'tx_hash': tx}

            if result['to'] == LP_contract:
                amt = float(result['value'])*1e-18
                output_dict[tx]['in amt'] = amt
                output_dict[tx]['address'] = result['from']
                    
                if result['tokenSymbol'] == top_pair:
                    token = top_pair
                    output_dict[tx]['in token'] = token
                    
                elif result['tokenSymbol'] == bottom_pair:
                    token = bottom_pair
                    output_dict[tx]['in token'] = token
                    
            elif result['from'] == LP_contract:
                amt = float(result['value'])*1e-18
                output_dict[tx]['out amt'] = amt
                output_dict[tx]['address'] = result['to']
                
                if result['tokenSymbol'] == top_pair:
                    token = top_pair
                    output_dict[tx]['out token'] = token
                    
                elif result['tokenSymbol'] == bottom_pair:
                    token = bottom_pair
                    output_dict[tx]['out token'] = token
                    
        except Exception as e:
            print(e)
                    
    df = pd.DataFrame.from_dict(output_dict, orient='index')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

    df = df[~(df['timestamp'] < '2021-09-06')]
    df = df.dropna()
    
    price_list = []
        
    for i, sell in enumerate(df['in token']):
        if sell == bottom_pair:
            price = df['in amt'].iloc[i] / df['out amt'].iloc[i]
        elif sell == top_pair:
            price = df['out amt'].iloc[i] / df['in amt'].iloc[i]
        price_list.append(price*decimal_ratio)
    
    df['price'] = price_list
    df = df.dropna().set_index('timestamp', drop=False)
    dt = pd.to_datetime(df['timestamp'], format='%Y/%m/%d %H:%M:%S')
    delta = pd.to_timedelta(df.groupby(dt).cumcount(), unit='ms')
    df['timestamp'] = dt + delta.values
    df = df.dropna().set_index('timestamp', drop=False)
    df = df.sort_index()
    print(df)
    
    # df = df.dropna().drop_duplicates(subset=['timestamp']).set_index('timestamp', drop=False)

    return df


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

    return df_top


r = redis.StrictRedis('localhost')
context = pa.default_serialization_context()


df = get_usd_dataset(get_all_LP_tx(GMX_ETH_LP, 'GMX', 'WETH', 1, 300000, 10), 
                     get_all_LP_tx(ETH_USDC_LP, 'WETH', 'USDC', 1e12, 100000, 30))
#print(df)
r.set('gmx-uniswap', context.serialize(df).to_buffer().to_pybytes())
#output = context.deserialize(r.get('api3-trending'))
#print(output)
