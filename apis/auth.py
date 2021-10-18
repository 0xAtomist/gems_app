import json
import os

script_dir = os.path.dirname(__file__)

# Load authentication
# rel_path_auth = '/home/lcm_fuelquality/auth_conf.json'
rel_path_auth = '../../auth_conf.json'
abs_path_auth = os.path.join(script_dir, rel_path_auth)
with open(abs_path_auth, 'r') as f:
    auth_conf = json.load(f)

auth_conf = auth_conf
