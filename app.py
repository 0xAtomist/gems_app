import dash
from dash.dependencies import Input, Output
from flask import Flask
import dash_bootstrap_components as dbc
from flask_caching import Cache
import flask_monitoringdashboard as dashboard

from auth import auth_conf


server = Flask(__name__)

#dashboard.bind(server)


app = dash.Dash(
    __name__,
    server=server,
    title='TokenFeeds',
    update_title=None,
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': "width=device-width, initial-scale=1"}],
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
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src="https://www.googletagmanager.com/gtag/js?id=G-JQ364K8SNP"></script>
        <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-JQ364K8SNP');
        </script>
    </head>
    <body>
        <div></div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
        <div></div>
    </body>
</html>
'''


app.css.config.serve_locally = True
app.server.secret_key = auth_conf['flask']['SECRET_KEY']

# Configure cache
cache = Cache(server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'localhost',
    'CACHE_REDIS_PORT': 6379,
#    'CACHE_REDIS_PASSWORD': auth_conf['redis']['password'],
    'CACHE_REDIS_DB': 1
})

#cache.clear()

