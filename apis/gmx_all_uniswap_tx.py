import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import redis
import pyarrow as pa


def get_all_LP_tx(LP_contract, top_pair, bottom_pair, decimal_ratio, blocklength, iterations):
    r_all = []
    for i in range(iterations):
        start = 300000+i*blocklength-1
        end = 300000+blocklength+i*blocklength+1
        r_page = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&address={}&startblock={}&endblock={}&sort=asc&apikey={}'
                            .format(LP_contract, start, end, API_key))
        #print(r_page.json()['result'][0])
        r_all.extend(r_page.json()['result'])
    
    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {}

    for i, result in enumerate(r_all):
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

    df = df[~(df['timestamp'] < '2021-09-06')]
    
    price_list = []
        
    for i, sell in enumerate(df['in token']):
        if sell == bottom_pair:
            price = df['in amt'].iloc[i] / df['out amt'].iloc[i]
        elif sell == top_pair:
            price = df['out amt'].iloc[i] / df['in amt'].iloc[i]
        price_list.append(price*decimal_ratio)
    
    df['price'] = price_list
    
    return df.dropna().drop_duplicates(subset=['timestamp']).set_index('timestamp', drop=False)


def get_usd_dataset(df_top, df_bottom):
    usd_list = []
    eth_list = []
    for i, dt in enumerate(df_top.index):
        idx = df_bottom.index.unique().get_loc(dt, method='nearest')
        ethusd_price = df_bottom['price'].iloc[idx]
        gmxusd_price = df_top['price'].iloc[i] * ethusd_price
        usd_list.append(gmxusd_price)
        eth_list.append(ethusd_price)
    
    df_top['usd_price'] = usd_list
    df_top['eth_price'] = eth_list
    # print(df_top)
    return df_top


df_usd = get_usd_dataset(get_all_LP_tx(GMX_ETH_LP, 'GMX', 'WETH', 1, 300000, 5), 
                         get_all_LP_tx(ETH_USDC_LP, 'WETH', 'USDC', 1e12, 100000, 15))

r = redis.StrictRedis('localhost')

context = pa.default_serialization_context()
r.set('gmx-uniswap', context.serialize(df).to_buffer().to_pybytes())

#output = context.deserialize(r.get('api3-trending'))
#print(output)
