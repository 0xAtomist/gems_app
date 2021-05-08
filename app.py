import dash
from flask import Flask
import dash_bootstrap_components as dbc
from flask_caching import Cache

from auth import auth_conf

server = Flask(__name__)

app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.title = 'GEMS Alliance: Performance'
app.server.secret_key = auth_conf['flask']['SECRET_KEY']

# Configure cache
cache = Cache(server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
#    'CACHE_REDIS_PASSWORD': auth_conf['redis']['password'],
    'CACHE_REDIS_DB': 1
})

cache.clear()


