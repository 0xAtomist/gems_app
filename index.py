import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
#import logging


from app import app, server
from apps import app1, inspect_app
from layouts import header, sidebar

from data_functions import get_gem_list, get_gem_info, get_filtered_df
from colours import palette, base_colours

master = get_gem_info()

content = html.Div(id="page-content", style={'padding-top': 5}) #, style=CONTENT_STYLE)


def serve_layout():
	return html.Div(
		[dcc.Location(id='url', refresh=False), sidebar.layout, header.layout, content],
		id='mainContainer',
	)

app.layout = serve_layout


@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_content(pathname):
    if pathname in ['/', '/gems-overview']:
        return app1.layout
    elif pathname == '/inspect-gem':
        return inspect_app.layout
    else:
        return dbc.Jumbotron([
            html.H1("404: Not found", style={'color': palette['red']['50']}),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised...")],
            className='pretty_container')

                
# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(Output(f"gems-page", "active"), [Input("url", "pathname")])
def toggle_active_links(pathname):
    #print(pathname)
    if pathname == "/":
        # Treat page 1 as the homepage / index
        return True
    elif pathname == "/gems-overview":
        return True
    else: return False


@app.callback(Output(f"inspect-page", "active"), [Input("url", "pathname")])
def toggle_active_links(pathname):
    if pathname == "/inspect-gem":
        return True
    else: return False


@app.callback(Output(f"trends-page", "active"), [Input("url", "pathname")])
def toggle_active_links(pathname):
    if pathname == "/trends":
        return True
    else: return False


@app.callback(Output(f"macro-page", "active"), [Input("url", "pathname")])
def toggle_active_links(pathname):
    if pathname == "/macro":
        return True
    else: return False


@app.callback(Output(f"wallet-page", "active"), [Input("url", "pathname")])
def toggle_active_links(pathname):
    if pathname == "/wallet":
        return True
    else: return False


@server.route('/api/v1/gems/all')
def api_gems():
    df = get_filtered_df(get_gem_list(master))
    json_msg = df.to_json(orient='split')
    return json_msg


if __name__ == "__main__":
	#gunicorn_logger = logging.getLogger('gunicorn.error')
	#app.logger.handlers = gunicorn_logger.handlers
	#app.logger.setLevel(gunicorn_logger.level)
	app.run_server(host='0.0.0.0', port=8000, debug=True)

