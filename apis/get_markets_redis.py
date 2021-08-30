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
context = pa.default_serialization_context()

for gem in gem_list:
    output = context.deserialize(r.get('{}-markets'.format(gem)))
    if 'KuCoin' in output['name'].values:
        print(gem)

