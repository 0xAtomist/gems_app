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


def get_all_staked_tx():
    r_all = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&contractaddress={}&address={}&startblock=0&endblock=2500000&sort=asc&apikey={}'
                        .format(GMX_contract, sGMX_contract, API_key))

    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out'])

    output_dict = {
        'value': [],
        'cum_value': [],
        'timestamp': [],
        'in/out': []
    }

    for result in r_all.json()['result']:
        if result['to'] == '0x908c4d94d34924765f1edc22a1dd098397c59dd4':
            value = float(float(result['value'])*1e-18)
            in_out = 'IN'
        else:
            value = -float(float(result['value'])*1e-18)
            in_out = 'OUT'
        timestamp = result['timeStamp']
        
        cum_value = 0

        output_dict['value'].append(value)
        output_dict['cum_value'].append(cum_value)
        output_dict['timestamp'].append(timestamp)
        output_dict['in/out'].append(in_out)


    df = pd.DataFrame.from_dict(output_dict) 
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
    df['Staked %'] = df['cum_value']/6490428*100

    df = df.dropna().drop_duplicates(subset=['timestamp']).set_index('timestamp', drop=False)

    return df


r = redis.StrictRedis('localhost')
context = pa.default_serialization_context()


df = get_all_staked_tx()
r.set('gmx-staked', context.serialize(df).to_buffer().to_pybytes())
#output = context.deserialize(r.get('api3-trending'))
#print(output)
