import sys
import os
import json
import time

from datetime import datetime
import requests
import pandas as pd
from pprint import pprint

from pycoingecko import CoinGeckoAPI

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


cg = CoinGeckoAPI()

coins_list = cg.get_coins_list()

coins_ids = []
ticker = 'moar'

for i, coin_dict in enumerate(coins_list):
    if coin_dict['symbol'] == ticker:
        coin_id = coin_dict['id']
        market = cg.get_coins_markets(
            ids=[coin_id],
            vs_currency='usd',
            price_change_percentage='1h,24h,7d',
            sparkline='true'
        )
        print(market)


