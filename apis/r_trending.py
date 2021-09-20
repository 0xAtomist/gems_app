import os, sys
import redis
import pandas as pd
import pyarrow as pa

import time
import json
import pickle

from api_functions import get_gem_info, get_gem_list, get_chart_data

# Get individual data
r = redis.StrictRedis('localhost')

gem_list = get_gem_list(get_gem_info())

gem_list.reverse()

for gem in list(gem_list):
    # Write inspection data
    df_max = get_chart_data(gem, 'max')
    time.sleep(1)
    diff_max = df_max.diff(axis=0)

    if diff_max['Datetime'][1] > pd.Timedelta(12, 'hours'):
        df_90 = get_chart_data(gem, 90)
        time.sleep(1)
        df = pd.concat([df_max.drop(df_max.index[-90:]), df_90])
        context = pa.default_serialization_context()
        r.set('{}-trending'.format(gem), context.serialize(df).to_buffer().to_pybytes())
    else:
        df = df_max
        context = pa.default_serialization_context()
        r.set('{}-trending'.format(gem), context.serialize(df).to_buffer().to_pybytes())



output = context.deserialize(r.get('api3-trending'))
print(output)

