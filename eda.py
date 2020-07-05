import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from navbar import Navbar
nav = Navbar()

body = dbc.Container(
    [
        dbc.Row(
        [
            dbc.Col(
                [
                    html.H2("Info"),
                    html.P(
                        """ This tool is to showing the H1B and PERM summary from year 2015 to 2019."""
                          ),
                          dbc.Button("View details", color="secondary"),
                ],
                md=4,
            ),
            dbc.Col(
                [
                    html.H2("Graph"),
                    dcc.Graph(
                        figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                           ),
                ]
            ),
        ]
        ),
    ],
    className="mt-4",
)

def EDA():
    layout = html.Div([
        nav,
	    body
    ])
    return layout

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = EDA()

if __name__ == "__main__":
    app.run_server()