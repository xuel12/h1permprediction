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
            html.H4("Please specify the base directory for PERM"),
            dbc.Input(id="input-on-submit-perm", placeholder=base_path, value=base_path, type="text"),
            html.Br(),
        ]),
        
        html.Div([
        # upload a new dataset out of default directory
        html.H4("Upload a new dataset"),
        dcc.Upload(
            id="upload-data-perm",
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
            html.Ul(id="file-list-perm")
        ], style={'font-size': '12px',}
        ),
    ]),
])

body = dbc.Container(
    [
        dcc.Markdown(children='''___'''),
        # Uploading all files
        html.H4("Process dataset"),
        html.Div(
            [
                dbc.Button("Start/Stop processing", id="submit-data-perm", n_clicks=0),
                dbc.Spinner(html.Div(id="submiting-data-perm")),
            ]
        ),
        html.Br(),
        
        # Create Div to place a invisible element inside
        html.Div([
            dcc.Input(id='upload-status-perm', value = 'stop'),
            dcc.Input(id = 'csvreader-status-perm',value = -1),
            dcc.Input(id='combinecsv-status-perm', value = 'wait'),
        ], style={'display': 'none'}
        ),

        # status indicators
        html.Div([        
            daq.Indicator(id='start-indicator-perm',label="Files Uploaded",value=True,color='grey'),
        ], style={'width': '30%', 'display': 'inline-block'}
        ),
        html.Div([
            daq.Indicator(id='xlsx2csv-indicator-perm',label="Parsing Files",value=True,color='grey'),
        ], style={'width': '30%', 'display': 'inline-block'}
        ),
        html.Div([        
            daq.Indicator(id='csvcombine-indicator-perm',label="Combining Data",value=True,color='grey'),
        ], style={'width': '30%', 'display': 'inline-block'}
        ),

         
        # dcc.Interval(id="progress-interval", n_intervals=0, interval=500),
        dbc.Progress(id="progress-perm"),       
        html.Div(id='parsing-status-perm', children='wait for input data'),  # add a section to store and display output
        html.Br(),
  
    ],
    className="mt-4",
)

train = dbc.Container([
    html.Div([
        dcc.Markdown(children='''___'''),
        # training
        html.H4("Train dataset"),
        html.P("Select date range for training"),
        html.Div([
            dcc.DatePickerRange(
                id='perm-date-picker-range',
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
                dbc.Button("Start/stop training", id="submit-training-perm", n_clicks=0),
                dbc.Spinner(html.Div(id="submiting-training-perm")),
            ]
        ),
        daq.Indicator(id='train-indicator-perm',label="Training Done",value=True,color='grey'),
        html.Br(),
    ])
])

def Training_perm():
    layout = html.Div(
    [
         nav,
         upload,
         body,
         train

    ],
    )
    return layout
