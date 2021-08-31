import os, sys
import redis
import pandas as pd
#import pyarrow as pa

import json
import pickle

from api_functions import get_gem_info, get_gem_list, get_api_markets, get_api_inspections, get_chart_data


# Get batch data

df = get_api_markets()
print(df)

r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)

for key in df.index:
    r_dict = df.loc[key].to_dict()
    r_dict['sparkline_in_7d'] = 0
    r.hmset(key, r_dict)

output = r.hgetall('api3')
print(output)
#df = pd.DataFrame.from_dict(output, orient='index')

