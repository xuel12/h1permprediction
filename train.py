#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:03:17 2020

@author: xuel12
"""

from datetime import datetime as dt

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_daq as daq
from navbar import Navbar

import constants

base_path = constants.BASE_PATH

nav = Navbar()

upload = dbc.Container([
        html.Div([
            # Specify directory,
            html.H4("Please specify the base directory"),
            dbc.Input(id="input-on-submit", placeholder=base_path, value=base_path, type="text"),
            html.Br(),
        ]),
        
        html.Div([
        # upload a new dataset out of default directory
        html.H4("Upload a new dataset"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to select a file to upload."]
            ),
            style={
                "width": "60%",
                "height": "40px",
                "lineHeight": "40px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            max_size=-1,
            multiple=True,
        ),
        
        # File list
        html.Div([
            html.H4("File List"),
            html.Ul(id="file-list")
        ], style={'font-size': '12px',}
        ),
    ]),
])

body = dbc.Container(
    [

        # Uploading all files
        html.H4("Process dataset"),
        html.Div(
            [
                dbc.Button("Start/Stop processing", id="submit-data", n_clicks=0),
                dbc.Spinner(html.Div(id="submiting-data")),
            ]
        ),
        
        # Create Div to place a invisible element inside
        html.Div([
            dcc.Input(id='upload-status', value = 'stop'),
            dcc.Input(id = 'csvreader-status',value = -1),
            dcc.Input(id='combinecsv-status', value = 'wait'),
        ], style={'display': 'none'}
        ),

        # status indicators
        html.Div([        
            daq.Indicator(id='start-indicator',label="Files Uploaded",value=True,color='grey'),
        ], style={'width': '30%', 'display': 'inline-block'}
        ),
        html.Div([
            daq.Indicator(id='xlsx2csv-indicator',label="Parsing Files",value=True,color='grey'),
        ], style={'width': '30%', 'display': 'inline-block'}
        ),
        html.Div([        
            daq.Indicator(id='csvcombine-indicator',label="Combining Data",value=True,color='grey'),
        ], style={'width': '30%', 'display': 'inline-block'}
        ),

         
        # dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
        dbc.Progress(id="progress"),       
        html.Div(id='parsing status', children='wait for input data'),  # add a section to store and display output
        html.Br(),
  
    ],
    className="mt-4",
)

train = dbc.Container([
    html.Div([
        # training
        html.H4("Train dataset"),
        html.Br(),
        html.P("Select date range for training"),
        html.Div([
            dcc.DatePickerRange(
                id='h1b-date-picker-range',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=dt(2030, 12, 31),
                initial_visible_month=dt(2020, 1, 1),
                # end_date=dt(2017, 8, 25).date()
            ),
            html.Div(id='date-picker-range'),
        ]),
        html.Br(),
        html.Div(
            [
                dbc.Button("Start/stop training", id="submit-training", n_clicks=0),
                dbc.Spinner(html.Div(id="submiting-training")),
            ]
        ),
        daq.Indicator(id='train-indicator',label="Training Done",value=True,color='grey'),
        html.Br(),
    ])
])

def Training():
    layout = html.Div(
    [
         nav,
         upload,
         body,
         train

    ],
    )
    return layout
