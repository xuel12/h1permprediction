import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import plotly
# import getpass
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

from navbar import Navbar

import pickle

import constants

os.chdir(constants.CODE_DIR)
base_path = constants.BASE_PATH
input_dir = constants.INPUT_DIR
if not os.path.exists(input_dir):
    os.makedirs(input_dir)
temp_dir = constants.TEMP_DIR
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)
model_dir = constants.MODEL_DIR
if not os.path.exists(model_dir):
    os.makedirs(model_dir)
download_dir = constants.DOWNLOAD_DIR
if not os.path.exists(download_dir):
    os.makedirs(download_dir)
    
nav = Navbar()

pickle_in = open(temp_dir + "eda.pickle","rb")

# if not os.path.exists(input_dir):
#     os.makedirs(input_dir)
edaplot = pickle.load(pickle_in)

# fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])
# fig = px.pie(edaplot['EMPLOYER_STATE'], values='CASE_STATUS', names='CASE_STATUS', title='Population of European continent')

fig_employter_state = go.Figure(data=[go.Pie(labels=edaplot['EMPLOYER_STATE'].index, 
                             values=edaplot['EMPLOYER_STATE']['CASE_STATUS'])])


body = dbc.Container(
    [
        html.P(
            """ This page is to showing the H1B and PERM summary from year 2015 to 2019."""
              ),
        # dbc.Button("View details", color="secondary"),
        
        dbc.Row(
        [
            dbc.Col(
                    [
                        html.H2("EMPLOYER_STATE"),
                        # dcc.Graph(
                        #     figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                        #        ),
                        dcc.Graph(
                            id='employer_state',
                            figure = fig_employter_state,
                        ),
                    ]
                ),
            dbc.Col(
                    [
                        html.H2("EMPLOYER_STATE"),
                        # dcc.Graph(
                        #     figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                        #        ),
                        dcc.Graph(
                            id='employer_state',
                            figure = fig_employter_state,
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