import requests
import pandas as pd
import time
import telegram
import redis
import sys

bot_key = '1857023695:AAGFDIotyZoy3_yFFhsbaASTVvibRIeJfXU'

api_id = '8307029'
api_hash = '3b18502f5287cfea4a2f1e1245e5753d'

chat_id = '-1001325583681'


bot = telegram.Bot(token=bot_key)

GMX_contract = "0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a"
sGMX_contract = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"

API_key = "YWR5E9YUBPE2X6KNXG99D2MX1UHPYDFDBGT"

pd.set_option('display.max_rows', 500)

offset = 500

def get_recent(interval):
    r_100 = requests.get('https://api.arbiscan.io/api?module=account&action=tokentx&contractaddress={}&address={}&page=1&offset={}&sort=desc&apikey={}'
                        .format(GMX_contract, sGMX_contract, offset, API_key))

    df = pd.DataFrame(columns=['value', 'timestamp', 'in/out', 'hash'])

    output_dict = {
        'value': [],
        'timestamp': [],
        'in/out': [],
        'hash': [],
    }

    for result in r_100.json()['result']:
        time_since = time.time() - float(result['timeStamp'])
        if time_since > interval:
            pass
        else:
            if result['to'] == '0x908c4d94d34924765f1edc22a1dd098397c59dd4':
                value = float(result['value'])*1e-18
                in_out = 'IN'
            else:
                value = -float(result['value'])*1e-18
                in_out = 'OUT'
            timestamp = result['timeStamp']
            tx_hash = result['hash']
            output_dict['value'].append(value)
            output_dict['timestamp'].append(timestamp)
            output_dict['in/out'].append(in_out)
            output_dict['hash'].append(tx_hash)

    df = pd.DataFrame.from_dict(output_dict) 
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
    df = df.drop_duplicates(subset=['hash'], keep=False)
    return df


def get_n_staked():
    r_staked = requests.get('https://api.arbiscan.io/api?module=account&action=tokenbalance&contractaddress={}&address={}&tag=latest&apikey={}'
                        .format(GMX_contract, sGMX_contract, API_key))
    return int(float(r_staked.json()['result'])*1e-18)


r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)

fish = '\U0001F41F'
shark = '\U0001F988'
whale = '\U0001F40B'

while True:
    try:
        print(time.time())
        df = get_recent(300)
        n_staked = get_n_staked()
        if df.empty:
            print('empty')
            pass
        else:
            print('Length: {}'.format(len(df.index)))
            for i, value in enumerate(df['value']):
                tx_hash = df['hash'].iloc[i]
                timestamp = str(df['timestamp'].iloc[i])
                if value < -2499 and value > -5000:
                    # send alert to TG bot
                    print('fish withdrawal')
                    print(str(df['timestamp'].iloc[i]))
                    entry = r.get(str(df['timestamp'].iloc[i]))
                    if not entry:
                        print('sending msg')
                        message = '{} ALERT: {} GMX has just been unstaked\n{} sGMX remaining\nTX Hash: https://arbiscan.io/tx/{}'.format(fish, int(-value), n_staked, tx_hash)
                        bot.send_message(chat_id=chat_id, text=message)
                        r.append(str(df['timestamp'].iloc[i]), value)
                elif value < -4999 and value > -25000:
                    # send alert to TG bot
                    print('shark withdrawal')
                    print(str(df['timestamp'].iloc[i]))
                    entry = r.get(str(df['timestamp'].iloc[i]))
                    if not entry:
                        print('sending msg')
                        message = '{} ALERT: {} GMX has just been unstaked\n{} sGMX remaining\nTX Hash: https://arbiscan.io/tx/{}'.format(shark, int(-value), n_staked, tx_hash)
                        bot.send_message(chat_id=chat_id, text=message)
                        r.append(str(df['timestamp'].iloc[i]), value)
                if value < -25000:
                    # send alert to TG bot
                    print('whale withdrawal')
                    print(str(df['timestamp'].iloc[i]))
                    entry = r.get(str(df['timestamp'].iloc[i]))
                    if not entry:
                        print('sending msg')
                        message = '{} ALERT: {} GMX has just been unstaked\n{} sGMX remaining\nTX Hash: https://arbiscan.io/tx/{}'.format(whale, int(-value), n_staked, tx_hash)
                        bot.send_message(chat_id=chat_id, text=message)
                        r.append(str(df['timestamp'].iloc[i]), value)
                else:
                    print('no large withdrawals')
        #print(time.time())
    except Exception as e:
        print(e)
    time.sleep(1)




