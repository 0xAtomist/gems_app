import os, sys
import redis
import pandas as pd
import pyarrow as pa

import time
import json
import pickle

from api_functions import get_gem_info, get_gem_list, get_api_markets, get_all_chart_data

# Get individual data
r = redis.StrictRedis('localhost')

gem_list = get_gem_list(get_gem_info())

for gem in gem_list:
    # Write inspection data
    df = get_all_chart_data(gem)
    context = pa.default_serialization_context()
    r.set('{}-trending'.format(gem), context.serialize(df).to_buffer().to_pybytes())


output = context.deserialize(r.get('api3-trending'))
print(output)

