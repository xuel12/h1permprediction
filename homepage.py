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

options_dict['EMPLOYER_STATE'] = constants.STATE_DROPDOWN
options_dict['WORKSITE_STATE'] = constants.STATE_DROPDOWN
options_dict['JOB_CATEGORY'] = list(set(constants.JOB_CATEGORY_DROPDOWN))
options_dict['JOB_LEVEL'] = list(set(constants.JOB_LEVEL_DROPDOWN))
options_dict['FULL_TIME_POSITION'] = list(set(constants.FULL_TIME_POSITION_DROPDOWN))
options_dict['PW_UNIT_OF_PAY'] = list(set(constants.PW_UNIT_OF_PAY_DROPDOWN))
options_dict['PW_WAGE_LEVEL'] = list(set(constants.PW_WAGE_LEVEL_DROPDOWN))
options_dict['H-1B_DEPENDENT'] = list(set(constants.H1B_DEPENDENT_DROPDOWN))
options_dict['WILLFUL_VIOLATOR'] = list(set(constants.WILLFUL_VIOLATOR_DROPDOWN))

options_dict['PERM_MODEL'] = ['Pre-trained', 'User-defined']
options_dict['PERM_WORKSITE_STATE'] = constants.STATE_DROPDOWN
options_dict['PERM_REFILE'] = list(set(constants.PERM_REFILE_DROPDOWN))
options_dict['PERM_FW_OWNERSHIP_INTEREST'] = list(set(constants.PERM_FW_OWNERSHIP_INTEREST_DROPDOWN))
options_dict['PERM_PW_LEVEL_9089'] = list(set(constants.PERM_PW_LEVEL_9089_DROPDOWN))
options_dict['PERM_JOB_INFO_EDUCATION'] = list(set(constants.PERM_JOB_INFO_EDUCATION_DROPDOWN))
options_dict['PERM_JOB_INFO_TRAINING'] = list(set(constants.PERM_JOB_INFO_TRAINING_DROPDOWN))
options_dict['PERM_JOB_INFO_ALT_FIELD'] = list(set(constants.PERM_JOB_INFO_ALT_FIELD_DROPDOWN))
options_dict['PERM_JOB_INFO_JOB_REQ_NORMAL'] = list(set(constants.PERM_JOB_INFO_JOB_REQ_NORMAL_DROPDOWN))
options_dict['PERM_JOB_INFO_FOREIGN_LANG_REQ'] = list(set(constants.PERM_JOB_INFO_FOREIGN_LANG_REQ_DROPDOWN))
options_dict['PERM_RECR_INFO_PROFESSIONAL_OCC'] = list(set(constants.PERM_RECR_INFO_PROFESSIONAL_OCC_DROPDOWN))
options_dict['PERM_RECR_INFO_COLL_UNIV_TEACHER'] = list(set(constants.PERM_RECR_INFO_COLL_UNIV_TEACHER_DROPDOWN))
options_dict['PERM_FW_INFO_BIRTH_COUNTRY'] = list(set(constants.PERM_FW_INFO_BIRTH_COUNTRY_DROPDOWN))
options_dict['PERM_CLASS_OF_ADMISSION'] = list(set(constants.PERM_CLASS_OF_ADMISSION_DROPDOWN))
options_dict['PERM_FW_INFO_TRAINING_COMP'] = list(set(constants.PERM_FW_INFO_TRAINING_COMP_DROPDOWN))


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

h1b = dbc.Container([
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
                daq.Indicator(id='predict-indicator', label="Red:Default Model, Blue:User Model",
                              value=True, color='red'),
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
    html.Br(),
    html.Br(),
    html.Br(),

    # dbc.Row(
    #         [
    #             html.Div(
    #                 [dcc.Graph(id="h1b_graph")],
    #                 className="pretty_container",
    #             ),
    #         ],
    #         ),
    ]
    # style=dict(display='flex')
)

    
    
perm = dbc.Container([
    html.H4("Predict new PERM application"),

    dbc.Row(
            [
            dbc.Col([
                html.Div("Select worksite state"),
                dcc.Dropdown(id = 'PERM_WORKSITE_STATE_dropdown', options = options['PERM_WORKSITE_STATE'], 
                             placeholder="Select worksite state", value = 'CA'),
                ]),
            dbc.Col([
                html.Div("Is it a refile?"),
                dcc.Dropdown(id = 'PERM_REFILE_dropdown', options = options['PERM_REFILE'], 
                             placeholder="Select refile or not", value = 'N'),
                ]),
            dbc.Col([
                html.Div("Does foreign worker has ownership interest?"),
                dcc.Dropdown(id = 'PERM_FW_OWNERSHIP_INTEREST_dropdown', options = options['PERM_FW_OWNERSHIP_INTEREST'], 
                             placeholder="Select ownership interest or not", value = 'N')
                ]),
            dbc.Col([
                html.Div("Select skill level"),
                dcc.Dropdown(id = 'PERM_PW_LEVEL_9089_dropdown', options = options['PERM_PW_LEVEL_9089'], 
                             placeholder="Select employer state", value = 'LEVEL II')
                ]),
            dbc.Col([
                html.Div("Select minimum education acceptable"),
                dcc.Dropdown(id = 'PERM_JOB_INFO_EDUCATION_dropdown', options = options['PERM_JOB_INFO_EDUCATION'], 
                             placeholder="Select minimum education", value = "MASTER'S")
                ]),
            ]
        ),
    html.Br(),
    dbc.Row(
            [dbc.Col([
                html.Div("Is training required?"),
                dcc.Dropdown(id = 'PERM_JOB_INFO_TRAINING_dropdown', options = options['PERM_JOB_INFO_TRAINING'], 
                             placeholder="Select training required or not", value = 'Y')
                ]),
            dbc.Col([
                html.Div("Is the alternative field acceptable?"),
                dcc.Dropdown(id = 'PERM_JOB_INFO_ALT_FIELD_dropdown', options = options['PERM_JOB_INFO_ALT_FIELD'], 
                             placeholder="Select accept alternative field or not", value = 'N')
                ]),
            dbc.Col([
                html.Div("Is job requirements are normal"),
                dcc.Dropdown(id = 'PERM_JOB_INFO_JOB_REQ_NORMAL_dropdown', options = options['PERM_JOB_INFO_JOB_REQ_NORMAL'], 
                             placeholder="Select job requirement normal or not", value = 'Y'),
                ]),
            dbc.Col([
                html.Div("Is foreign language required?"),
                dcc.Dropdown(id = 'PERM_JOB_INFO_FOREIGN_LANG_REQ_dropdown', options = options['PERM_JOB_INFO_FOREIGN_LANG_REQ'], 
                             placeholder="Select foreign language required or not", value = 'N'),
                ]),
            dbc.Col([
                html.Div("Is it for a professional occupation?"),
                dcc.Dropdown(id = 'PERM_RECR_INFO_PROFESSIONAL_OCC_dropdown', options = options['PERM_RECR_INFO_PROFESSIONAL_OCC'], 
                             placeholder="Select professional occupation or not", value = 'Y'),
                ]),
            ]
        ),
    html.Br(),
    dbc.Row(
            [dbc.Col([
                html.Div("Apply for a college teacher?"),
                dcc.Dropdown(id = 'PERM_RECR_INFO_COLL_UNIV_TEACHER_dropdown', options = options['PERM_RECR_INFO_COLL_UNIV_TEACHER'], 
                             placeholder="Select college teacher or not", value = 'N')
                ]),
            dbc.Col([
                html.Div("Birth country?"),
                dcc.Dropdown(id = 'PERM_FW_INFO_BIRTH_COUNTRY_dropdown', options = options['PERM_FW_INFO_BIRTH_COUNTRY'], 
                             placeholder="Select worker birth country", value = 'INDIA')
                ]),
            dbc.Col([
                html.Div("Visa class"),
                dcc.Dropdown(id = 'PERM_CLASS_OF_ADMISSION_dropdown', options = options['PERM_CLASS_OF_ADMISSION'], 
                             placeholder="Select visa class", value = 'H-1B'),
                ]),
            dbc.Col([
                html.Div("Is the training done?"),
                dcc.Dropdown(id = 'PERM_FW_INFO_TRAINING_COMP_dropdown', options = options['PERM_FW_INFO_TRAINING_COMP'], 
                             placeholder="Select foreign worker training complete or not",
                             value = 'A'),
                ]),
            ]
        ),
    
    html.Br(),
    dbc.Row(
            [dbc.Col([
                html.Div("Model to use"),
                dcc.Dropdown(id = 'PERM_MODEL_dropdown', options = options['PERM_MODEL'], 
                             placeholder="Select a model to use", value = 'Pre-trained'),
                ]),
            dbc.Col([
                # html.Div("Model to use"),
                daq.Indicator(id='predict-indicator-perm', label="Red:Default Model, Blue:User Model",
                              value=True, color='red'),
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
            dbc.Button("Start/Reset prediction", id="submit-predict-perm", n_clicks=0),
            ]),
        dbc.Col([
            dbc.Spinner(html.Div(id="submitting-predict-perm")),
            ]),
        ]
        ),
        
    # prediction graph
    html.Br(),
    html.Div(id='my-output-perm'),

    # dbc.Row(
    #         [
    #             html.Div(
    #                 [dcc.Graph(id="h1b_graph")],
    #                 className="pretty_container",
    #             ),
    #         ],
    #         ),
    ]
    # style=dict(display='flex')
)

def Homepage():
    layout = html.Div([
        nav,
	    body,
        h1b,
        perm
    ])
    return layout

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = Homepage()


    

    
if __name__ == "__main__":
    app.run_server()