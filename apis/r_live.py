import os, sys
import redis
import pandas as pd
import json
import pickle

from api_functions import get_gem_list, get_api_markets

df = get_api_markets()

r = redis.StrictRedis('localhost', charset='utf-8', decode_responses=True)

print(df.loc['bitcoin'])

for key in df.index:
	print(key)
	r_dict = df.loc[key].to_dict()
	print(r_dict)
	r.hmset(key, r_dict)

output = r.hgetall('mainframe')
#decoded = {key.decode('utf-8'):value.decode('utf-8') for key, value in output.items()}
print(output)
df = pd.DataFrame.from_dict(output, orient='index')
print(df)


