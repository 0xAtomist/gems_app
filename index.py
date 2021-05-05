import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import app1
from layouts import header, sidebar


content = html.Div(id="page-content", style={'padding-top': 5}) #, style=CONTENT_STYLE)

def serve_layout():
	return html.Div(
		[dcc.Location(id='url', refresh=False), sidebar.layout, header.layout, content],
		id='mainContainer',
	)

app.layout = serve_layout


@app.callback(
	Output("page-content", "children"),
	[Input("url", "pathname")]
)
def render_page_content(pathname):
	if pathname in ["/app/", "/app/gems-overview"]:
		return app1.layout
	else:
		return dbc.Jumbotron([
			html.H1("404: Not found", className="text-danger"),
			html.Hr(),
			html.P(f"The pathname {pathname} was not recognised...")])


if __name__ == "__main__":
	gunicorn_logger = logging.getLogger('gunicorn.error')
	app.logger.handlers = gunicorn_logger.handlers
	app.logger.setLevel(gunicorn_logger.level)
	app.run_server(host='0.0.0.0', port=8050, debug=True)
