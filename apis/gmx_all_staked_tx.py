import requests
import pandas as pd
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


def get_all_staked_tx(blocklength, iterations):
    r_all = []
    for i in range(iterations):
        start = 300000+i*blocklength-1
        end = 300000+blocklength+i*blocklength+1
    r_page = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&contractaddress={}&address={}&startblock={}&endblock={}&sort=asc&apikey={}'
                        .format(GMX_contract, sGMX_contract, API_key))
    r_all.extend(r_page.json()['result'])

    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {
        'value': [],
        'cum_value': [],
        'timestamp': [],
        'in/out': []
    }

    for result in r_all.json()['result']:
        tx = result['hash']
        timestamp = result['timeStamp']
        blocknumber = result['blockNumber']
        
        output_dict[tx] = {'timestamp': timestamp, 'blocknumber': blocknumber, 'tx_hash': tx}
        
        if result['to'] == '0x908c4d94d34924765f1edc22a1dd098397c59dd4':
            value = float(float(result['value'])*1e-18)
            in_out = 'IN'
        else:
            value = -float(float(result['value'])*1e-18)
            in_out = 'OUT'
        
        cum_value = 0

        output_dict[tx]['value'].append(value)
        output_dict[tx]['cum_value'].append(cum_value)
        output_dict[tx]['timestamp'].append(timestamp)
        output_dict[tx]['in/out'].append(in_out)


    df = pd.DataFrame.from_dict(output_dict, orient='index') 
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

    df = df.dropna()

    df = df.dropna().set_index('timestamp', drop=False)
    dt = pd.to_datetime(df['timestamp'], format='%Y/%m/%d %H:%M:%S')
    delta = pd.to_timedelta(df.groupby(dt).cumcount(), unit='ms')
    df['timestamp'] = dt + delta.values
    df = df.dropna().set_index('timestamp', drop=False)
    df = df.sort_index()
    print(df)
    return df


def get_n_staked():
    r_staked = requests.get('https://api.arbiscan.io/api?module=account&action=tokenbalance&contractaddress={}&address={}&tag=latest&apikey={}'
                        .format(GMX_contract, sGMX_contract, API_key))
    return int(float(r_staked.json()['result'])*1e-18)



def get_n_total():
    r_total = requests.get('https://api.arbiscan.io/api?module=stats&action=tokensupply&contractaddress={}&tag=latest&apikey={}'
                        .format(GMX_contract, API_key))
    return int(float(r_total.json()['result'])*1e-18)


r = redis.StrictRedis('localhost')
context = pa.default_serialization_context()


df = get_all_staked_tx(300000, 10)
n_total = get_n_total()
df['Staked %'] = df['cum_value']/n_total*100
r.set('gmx-staked', context.serialize(df).to_buffer().to_pybytes())
#output = context.deserialize(r.get('api3-trending'))
#print(output)
