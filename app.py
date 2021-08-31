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
    external_stylesheets=[dbc.themes.BOOTSTRAP, "https://tools.aftertheflood.com/sparks/styles/font-faces.css"]
)


app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3415489682836828"
            crossorigin="anonymous"></script>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <div>My Custom header</div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div>My Custom footer</div>
    </body>
</html>
'''


app.css.config.serve_locally = True
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
