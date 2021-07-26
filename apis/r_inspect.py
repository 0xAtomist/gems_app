import os, sys
import redis
import pandas as pd
import pyarrow as pa

import time
import json
import pickle

from api_functions import get_gem_info, get_gem_list, get_api_inspections, get_chart_data

# Get individual data
r = redis.StrictRedis('localhost')

gem_list = get_gem_list(get_gem_info())

for gem in gem_list:
    # Write inspection data
    df_inspect, dff_inspect = get_api_inspections(gem)
    context = pa.default_serialization_context()
    r.set('{}-inspect'.format(gem), context.serialize(df_inspect).to_buffer().to_pybytes())

    context = pa.default_serialization_context()
    r.set('{}-markets'.format(gem), context.serialize(dff_inspect).to_buffer().to_pybytes())

    # Write chart data
    for period in [1, 7, 14, 30, 90, 180, 365, 'max']:
        df = get_chart_data(gem, period)
        time.sleep(1)
        context = pa.default_serialization_context()
        r.set('{}-{}d-chart'.format(gem, period), context.serialize(df).to_buffer().to_pybytes())


output = context.deserialize(r.get('api3-inspect'))
print(output)
output = context.deserialize(r.get('api3-markets'))
print(output)
output = context.deserialize(r.get('api3-30d-chart'))
print(output)

