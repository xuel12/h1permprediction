#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:03:17 2020

@author: xuel12
"""

### Data
import pandas as pd
import pickle

### Graphing
import plotly.graph_objects as go

### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import dash_daq as daq

## Navbar
from navbar import Navbar

import os
BASE_DIR = "/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/"
CODE_DIR = BASE_DIR+"h1permprediction/"
os.chdir(CODE_DIR)

import constants

temp_dir = constants.TEMP_DIR

df = pd.read_csv(temp_dir+'h1b2015to2020_sub.csv')
# df.iloc[1:10000].to_csv(temp_dir+'h1b2015to2020_sub.csv')

options_dict = {}
options_dict['EMPLOYER_STATE'] = list(set(constants.US_STATE_ABBREV.values()))
options_dict['EMPLOYER_COUNTRY'] = df['EMPLOYER_COUNTRY'].unique().tolist()
options_dict['JOB_TITLE'] = df['JOB_TITLE'].unique().tolist()
options_dict['WORKSITE_STATE'] = list(set(constants.US_STATE_ABBREV.values()))
options_dict['JOB_CATEGORY'] = df['JOB_CATEGORY'].unique().tolist()
options_dict['JOB_LEVEL'] = df['JOB_LEVEL'].unique().tolist()
options_dict['FULL_TIME_POSITION'] = df['FULL_TIME_POSITION'].unique().tolist()
options_dict['PW_UNIT_OF_PAY'] = df['PW_UNIT_OF_PAY'].unique().tolist()
options_dict['PW_WAGE_LEVEL'] = df['PW_WAGE_LEVEL'].unique().tolist()
options_dict['H-1B_DEPENDENT'] = df['H-1B_DEPENDENT'].unique().tolist()

options = {}
for key in options_dict:
    options[key] = [{'label':x, 'value': x} for x in options_dict[key]]


# df.set_index(df.iloc[:,0], drop = True, inplace = True)
# df = df.iloc[:,1:]

nav = Navbar()

body = dbc.Container(
    [
        html.Div([
            dbc.Row([html.H1("PREDICTION FOR H-1B & PERM")], justify="center", align="center", className="h-50"),
            dbc.Row([html.P('A dashboard for predicting success rate of H1B and PERM')], justify="center", align="center", className="h-50"),
            html.Br(),
        ]
        ),
        
        # prediction
        html.H4("Predict new batch"),
        html.Div(
            [
                dbc.Button("Start/stop prediction", id="submit-predict", n_clicks=0),
                dbc.Spinner(html.Div(id="submiting-predict")),
            ]
        ),
        daq.Indicator(id='predict-indicator',label="Prediction Done",value=True,color='grey'),
        html.Br(),
    ],
    className="mt-4",
)

dropdown = dbc.Container([
    
    dbc.Row(
            [dbc.Col([
                html.Div("Select employer country"),
                dcc.Dropdown(id = 'EMPLOYER_COUNTRY_dropdown', options = options['EMPLOYER_COUNTRY'], 
                             placeholder="Select employer country")
                ]),
            dbc.Col([
                html.Div("Select employer state"),
                dcc.Dropdown(id = 'EMPLOYER_STATE_dropdown', options = options['EMPLOYER_STATE'], 
                             placeholder="Select employer state")
                ]),
            dbc.Col([
                html.Div("Select worksite state"),
                dcc.Dropdown(id = 'WORKSITE_STATE_dropdown', options = options['WORKSITE_STATE'], 
                             placeholder="Select worksite state"),
                ]),
            dbc.Col([
                html.Div("Select job category"),
                dcc.Dropdown(id = 'JOB_CATEGORY_dropdown', options = options['JOB_CATEGORY'], 
                             placeholder="Select job category"),
                ]),
            ]
        ),
    html.Br(),
    dbc.Row(
            [dbc.Col([
                html.Div("Job level"),
                dcc.Dropdown(id = 'JOB_LEVEL_dropdown', options = options['JOB_LEVEL'], 
                             placeholder="Select job level")
                ]),
            dbc.Col([
                html.Div("Full-time position?"),
                dcc.Dropdown(id = 'EMPLOYER_STATE_dropdown', options = options['FULL_TIME_POSITION'], 
                             placeholder="Select full-time position or not")
                ]),
            dbc.Col([
                html.Div("Wage level"),
                dcc.Dropdown(id = 'PW_WAGE_LEVEL_dropdown', options = options['PW_WAGE_LEVEL'], 
                             placeholder="Select wage level"),
                ]),
            dbc.Col([
                html.Div("Is there H-1B_DEPENDENT?"),
                dcc.Dropdown(id = 'H-1B_DEPENDENT_dropdown', options = options['H-1B_DEPENDENT'], 
                             placeholder="Select h1b dependent"),
                ]),
            ]
        ),
    ],
    # style=dict(display='flex')
)

def Homepage():
    layout = html.Div([
        nav,
	    body,
        dropdown,
    ])
    return layout

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = Homepage()

if __name__ == "__main__":
    app.run_server()