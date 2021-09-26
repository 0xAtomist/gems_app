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


def get_recent_LP_tx(LP_contract, top_pair, bottom_pair, decimal_ratio):
    r_all = []
    r_100 = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&address={}&page=1&offset=100&sort=desc&apikey={}'
                        .format(LP_contract, API_key))
    
    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {}

    for i, result in enumerate(r_100.json()['result']):
        tx = result['hash']
        timestamp = result['timeStamp']
        blocknumber = result['blockNumber']
        
        if tx in output_dict.keys():
            pass
        else:
            output_dict[tx] = {'timestamp': timestamp, 'blocknumber': blocknumber}


        if result['to'] == LP_contract:
            in_out = 'in'
            
            if result['tokenSymbol'] == top_pair:
                token = top_pair
                amt = float(result['value'])*1e-18
                output_dict[tx]['in amt'] = amt
                output_dict[tx]['in token'] = token
                
            elif result['tokenSymbol'] == bottom_pair:
                token = bottom_pair
                amt = float(result['value'])*1e-18
                output_dict[tx]['in amt'] = amt
                output_dict[tx]['in token'] = token
        elif result['from'] == LP_contract:
            in_out = 'out'
            
            if result['tokenSymbol'] == top_pair:
                token = top_pair
                amt = float(result['value'])*1e-18
                output_dict[tx]['out amt'] = amt
                output_dict[tx]['out token'] = token
                
            elif result['tokenSymbol'] == bottom_pair:
                token = bottom_pair
                amt = float(result['value'])*1e-18
                output_dict[tx]['out amt'] = amt
                output_dict[tx]['out token'] = token
                    
    df = pd.DataFrame.from_dict(output_dict, orient='index')
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    

    # df = df[~(df['timestamp'] < '2021-09-06')]
    
    price_list = []
        
    for i, sell in enumerate(df['in token']):
        if sell == bottom_pair:
            price = df['in amt'].iloc[i] / df['out amt'].iloc[i]
        elif sell == top_pair:
            price = df['out amt'].iloc[i] / df['in amt'].iloc[i]
        price_list.append(price*decimal_ratio)
    
    df['price'] = price_list
    df = df.dropna().drop_duplicates(subset=['timestamp']).set_index('timestamp', drop=False)
    
    return df


def get_usd_dataset(df_top, df_bottom):
    usd_list = []
    eth_list = []
    vol_list = []
    for i, dt in enumerate(df_top.index):
        idx = df_bottom.index.unique().get_loc(dt, method='nearest')
        ethusd_price = df_bottom['price'].iloc[idx]
        gmxusd_price = df_top['price'].iloc[i] * ethusd_price
        usd_list.append(gmxusd_price)
        eth_list.append(ethusd_price)
        if df_top['in token'].iloc[i] == 'GMX':
            vol = df_top['in amt'].iloc[i] * gmxusd_price
        elif df_top['in token'].iloc[i] == 'WETH':
            vol = df_top['in amt'].iloc[i] * ethusd_price
        vol_list.append(vol)


    df_top['usd_price'] = usd_list
    df_top['eth_price'] = eth_list
    df_top['volume'] = vol_list
    return df_top


r = redis.StrictRedis('localhost')
context = pa.default_serialization_context()


while True:
    # get recent txns
    try:
        df_100 = get_usd_dataset(get_recent_LP_tx(GMX_ETH_LP, 'GMX', 'WETH', 1),
                                 get_recent_LP_tx(ETH_USDC_LP, 'WETH', 'USDC', 1e12))
        print(df_100)
        
        for i, timestamp in enumerate(df_100['timestamp']):
            df_all = context.deserialize(r.get('gmx-uniswap'))
            if timestamp in df_all.index:
                print('already stored')
                pass
            else:
                print('requires storing')
                df_all = df_all.append(df_100.iloc[i])
                r.set('gmx-uniswap', context.serialize(df_all).to_buffer().to_pybytes())
    except Exception as e:
        print(e)
    time.sleep(10)

