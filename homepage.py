#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:03:17 2020

@author: xuel12
"""

### Data
import pandas as pd
import numpy as np
import pickle
import time

### Graphing
import plotly.graph_objects as go

### Dash
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
import dash_daq as daq

## Navbar
from navbar import Navbar

import os
BASE_DIR = "/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/"
CODE_DIR = BASE_DIR+"h1permprediction/"
os.chdir(CODE_DIR)

import constants

temp_dir = constants.TEMP_DIR
model_dir = constants.MODEL_DIR

# load data and model
df = pd.read_csv(temp_dir+'h1b2015to2020_sub.csv')
    
# df.iloc[1:10000].to_csv(temp_dir+'h1b2015to2020_sub.csv')

options_dict = {}
options_dict['MODEL'] = ['Pre-trained', 'User-defined']
# options_dict['EMPLOYER_STATE'] = list(set(constants.US_STATE_ABBREV.values()))
# options_dict['WORKSITE_STATE'] = list(set(constants.US_STATE_ABBREV.values()))
# options_dict['JOB_CATEGORY'] = df['JOB_CATEGORY'].unique().tolist()
# options_dict['JOB_LEVEL'] = df['JOB_LEVEL'].unique().tolist()
# options_dict['FULL_TIME_POSITION'] = df['FULL_TIME_POSITION'].unique().tolist()
# options_dict['PW_UNIT_OF_PAY'] = df['PW_UNIT_OF_PAY'].unique().tolist()
# options_dict['PW_WAGE_LEVEL'] = df['PW_WAGE_LEVEL'].unique().tolist()
# options_dict['H-1B_DEPENDENT'] = df['H-1B_DEPENDENT'].unique().tolist()
# options_dict['WILLFUL_VIOLATOR'] = df['WILLFUL_VIOLATOR'].unique().tolist()

options_dict['EMPLOYER_STATE'] = list(set(constants.US_STATE_ABBREV.values()))
options_dict['WORKSITE_STATE'] = list(set(constants.US_STATE_ABBREV.values()))
options_dict['JOB_CATEGORY'] = list(set(constants.JOB_CATEGORY_DROPDOWN))
options_dict['JOB_LEVEL'] = list(set(constants.JOB_LEVEL_DROPDOWN))
options_dict['FULL_TIME_POSITION'] = list(set(constants.FULL_TIME_POSITION_DROPDOWN))
options_dict['PW_UNIT_OF_PAY'] = list(set(constants.PW_UNIT_OF_PAY_DROPDOWN))
options_dict['PW_WAGE_LEVEL'] = list(set(constants.PW_WAGE_LEVEL_DROPDOWN))
options_dict['H-1B_DEPENDENT'] = list(set(constants.H1B_DEPENDENT_DROPDOWN))
options_dict['WILLFUL_VIOLATOR'] = list(set(constants.WILLFUL_VIOLATOR_DROPDOWN))


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
    
        
    ],
    className="mt-4",
)

dropdown = dbc.Container([
    html.H4("Predict new H1B application"),

    dbc.Row(
            [dbc.Col([
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
            dbc.Col([
                html.Div("Job level"),
                dcc.Dropdown(id = 'JOB_LEVEL_dropdown', options = options['JOB_LEVEL'], 
                             placeholder="Select job level")
                ]),
            ]
        ),
    html.Br(),
    dbc.Row(
            [dbc.Col([
                html.Div("Full-time position?"),
                dcc.Dropdown(id = 'FULL_TIME_POSITION_dropdown', options = options['FULL_TIME_POSITION'], 
                             placeholder="Select full-time position or not")
                ]),
            dbc.Col([
                html.Div("Wage unit of pay?"),
                dcc.Dropdown(id = 'PW_UNIT_OF_PAY_dropdown', options = options['PW_UNIT_OF_PAY'], 
                             placeholder="Select wage unit of pay")
                ]),
            dbc.Col([
                html.Div("Wage level"),
                dcc.Dropdown(id = 'PW_WAGE_LEVEL_dropdown', options = options['PW_WAGE_LEVEL'], 
                             placeholder="Select wage level"),
                ]),
            dbc.Col([
                html.Div("Is there a dependent?"),
                dcc.Dropdown(id = 'H-1B_DEPENDENT_dropdown', options = options['H-1B_DEPENDENT'], 
                             placeholder="Select h1b dependent"),
                ]),
            dbc.Col([
                html.Div("Willful violator?"),
                dcc.Dropdown(id = 'WILLFUL_VIOLATOR_dropdown', options = options['WILLFUL_VIOLATOR'], 
                             placeholder="Select willful violator of not"),
                ]),
            ]
        ),
    
    html.Br(),
    dbc.Row(
            [dbc.Col([
                html.Div("Model to use"),
                dcc.Dropdown(id = 'MODEL_dropdown', options = options['MODEL'], 
                             placeholder="Select a model to use", value = 'Pre-trained'),
                ]),
            dbc.Col([
                # html.Div("Model to use"),
                daq.Indicator(id='predict-indicator', label="Progress",value=True,color='grey'),
                ]),
            ]),
    # prediction
    html.Br(),
    # html.Div(
    #     [
    #         dbc.Button("Start/Reset prediction", id="submit-predict", n_clicks=0),
    #         dbc.Spinner(html.Div(id="submitting-predict")),
    #     ]
    # ),
    dbc.Row([
        dbc.Col([
            dbc.Button("Start/Reset prediction", id="submit-predict", n_clicks=0),
            ]),
        dbc.Col([
            dbc.Spinner(html.Div(id="submitting-predict")),
            ]),
        ]
        ),
        
    # prediction graph
    html.Br(),
    html.Div(id='my-output'),

    dbc.Row(
            [
                html.Div(
                    [dcc.Graph(id="h1b_graph")],
                    className="pretty_container",
                ),
            ],
            ),
    ]
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