import os, sys
import redis
import pandas as pd
import pyarrow as pa

from api_functions import get_gem_list, get_btc_history

df = get_btc_history()

r = redis.StrictRedis('localhost')

context = pa.default_serialization_context()
r.set('btc_history', context.serialize(df).to_buffer().to_pybytes())
output = context.deserialize(r.get('btc_history'))
print(output)


#df = pd.DataFrame.from_dict(output, orient='index')
#print(df)


