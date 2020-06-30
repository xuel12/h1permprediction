#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 15:03:17 2020

@author: xuel12
"""

import base64
import io
import os
# import sys
import re
import glob
import time
from urllib.parse import quote as urlquote
import subprocess

from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_daq as daq

import pandas as pd

# BASE_DIR = "/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/"
# CODE_DIR = BASE_DIR+"h1permprediction/"
# os.chdir(CODE_DIR)

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

# try: 
#     default_train_df = pd.read_csv(temp_dir + 'bigcsv.csv')
#     print("Current directory is {}".format(os.getcwd()))
# except: 
#     print("Something wrong with specified directory. Exception- ", sys.exc_info())
    
    
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets=[dbc.themes.BOOTSTRAP]

# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__)



@server.route(constants.DOWNLOAD_DIR + "<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(input_dir, path, as_attachment=True)


app.layout = html.Div(
    [
        # App name and description
        html.Div([
            dbc.Row([html.H1("PREDICTION FOR H-1B & PERM")], justify="center", align="center", className="h-50"),
            dbc.Row([html.P('A dashboard for predicting success rate of H1B and PERM')], justify="center", align="center", className="h-50"),
            html.Br(),
        ]
        ),
        
        # Specify directory,
        html.H4("Please specify the base directory"),
        html.Div([
            dbc.Input(id="input-on-submit", placeholder=base_path, value=base_path, type="text"),
            html.Br(),
        ]),
        
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

        # training
        html.H4("Train dataset"),
        html.Div(
            [
                dbc.Button("Start/stop training", id="submit-training", n_clicks=0),
                dbc.Spinner(html.Div(id="submiting-training")),
            ]
        ),
        daq.Indicator(id='train-indicator',label="Training Done",value=True,color='grey'),
        html.Br(),

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

    ],style={'marginLeft': 10, 'marginRight': 10, 'marginTop': 10, 'marginBottom': 10, 
               # 'backgroundColor':'#F7FBFE', 'border': 'thin lightgrey dashed', 
               "max-width": "1000px", 'padding': '6px 0px 0px 8px'},
)


                 
@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]
    

@app.callback(
    [Output('start-indicator', 'color'), Output("submiting-data", "children")],
    [Input("submit-data", "n_clicks")])
def start_indicator(n_clicks):
    if n_clicks:
        time.sleep(1)
    if n_clicks % 2 == 1:
        color = 'blue'
    else:
        color = 'grey'
    return color, ""


@app.callback(
    Output('csvreader-status', 'value'),
    # [Output("progress", "value"), Output("progress", "children")],
    # specify the component and its property that shall contain the output
    [Input('start-indicator', 'color')],
    # specify the component and corresponding properties that shall serve as input
    [State('input-on-submit','value')]) 
    # specify the component and corresponding properties that shall serve as input
def update_data(color, base_path):  # define the function reaching output from input
    if color == 'blue':
        # BASE_PATH = value  # input value gives the base directory
        input_dir = folderStruct(base_path)['input_dir']

        # convert xlsx to csv for faster process        
        count_newcsv = xlsx2csv(input_dir)
        # count_newcsv = 0
        # return progress, f"{progress} %" if progress >= 5 else ""
        return count_newcsv
    else:
        return -1


@app.callback(
    Output('xlsx2csv-indicator', 'color'),
    # specify the component and its property that shall contain the output
    [Input('csvreader-status', 'value')])
def xlsx2csv_indicator(status):
    if status != -1:
        color = 'orange'
    else:
        color = 'grey'
    return color


@app.callback(
    [Output('parsing status', 'children'), Output('combinecsv-status', 'value')],
    # specify the component and its property that shall contain the output
    [Input('csvreader-status', 'value')],
    [State('input-on-submit','value')]) 
def update_combinedata(count_newcsv, value):  # define the function reaching output from input
    if count_newcsv != -1:
        temp_dir = folderStruct(base_path)['temp_dir']
        input_dir = folderStruct(base_path)['input_dir']

        # read in csv to dataframe
        if count_newcsv > 0 or not os.path.exists(temp_dir+'bigcsv.csv'):
            csvCombine(input_dir, temp_dir)
            
        finish_message = 'Data parsing complete, find the parsed combineCSV in directory'
        # return progress, f"{progress} %" if progress >= 5 else ""
        return finish_message, 'done'
    else:
        return '', 'wait'


@app.callback(
    Output('csvcombine-indicator', 'color'),
    # specify the component and its property that shall contain the output
    [Input('combinecsv-status', 'value')])
def csvcombine_indicator(status):
    if status == 'done':
        color = 'red'
    else:
        color = 'grey'
    return color
    
    
@app.callback(
    [Output("progress", "value"), Output("progress", "children")],
    [Input('start-indicator', 'color'),
     Input('xlsx2csv-indicator', 'color'), Input('csvcombine-indicator', 'color')],
)
def data_progress(start_color, xlsx2csv_indicator, csvcombine_indicator):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    if csvcombine_indicator != 'grey':
        progress = 100
    elif xlsx2csv_indicator != 'grey':
        progress = 70
    elif start_color != 'grey':
        progress = 20
    else:
        progress = 0

    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else "" 

       
def save_file(filename, content):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)
    try:
        filename_csv = os.path.splitext(filename)[0]+'.csv'
        if not os.path.exists(input_dir+filename_csv):
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xlsx' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
            df.to_csv(input_dir+filename_csv, index=False) 
            print('File added to database.')
        else:
            print('File exists.')
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(input_dir):
        path = os.path.join(input_dir, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = download_dir+"{}".format(urlquote(filename))
    return html.A(filename, href=location)

    
def folderStruct(BASE_PATH):
    CODE_DIR = BASE_PATH + "h1permprediction/"
    INPUT_DIR = BASE_PATH + "input/"
    # PREDICT_DIR = BASE_PATH + "predict/"
    TEMP_DIR = BASE_PATH + "temp/"
    MODEL_DIR = BASE_PATH + "model/"
    # OUTPUT_DIR = BASE_PATH + "output/"
    DOWNLOAD_DIR = BASE_PATH + "download/"

    os.chdir(CODE_DIR)
    # base_path = BASE_PATH
    input_dir = INPUT_DIR
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    temp_dir = TEMP_DIR
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    model_dir = MODEL_DIR
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    download_dir = DOWNLOAD_DIR
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    return {'input_dir':input_dir, 'temp_dir':temp_dir, 'model_dir':model_dir,
            'download_dir':download_dir, 'BASE_PATH':BASE_PATH, 'CODE_DIR':CODE_DIR} 


# convert xlsx to csv
def xlsx2csv(in_dir):
    xlsx_path = in_dir
    csv_path = in_dir
    list_of_xlsx = glob.glob(xlsx_path+'*.xlsx')
    
    count_newcsv = 0
    for xlsx in list_of_xlsx:
        # Extract File Name on group 2 "(.+)"
        filename = re.search(r'(.+[\\|\/])(.+)(\.(xlsx))', xlsx).group(2)
        if not os.path.exists(csv_path+filename+'.csv'):
            # Setup the call for subprocess.call()
            call = ["python", "./xlsx2csv.py", xlsx, csv_path+filename+'.csv']
            try:
                subprocess.call(call) # On Windows use shell=True
            except:
                print('Failed with {}'.format(xlsx_path))
            count_newcsv = count_newcsv + 1
    return count_newcsv
                

# read each csv to df and then concatenate
def csvCombine(in_dir, temp_dir):
    outputcsv = temp_dir+'bigcsv.csv' #specify filepath+filename of output csv
    csv_path = in_dir

    listofdataframes = []
    for file in glob.glob(csv_path+'*.csv'):
        df = pd.read_csv(file)
        if df.shape[1] > 0: # make sure there are columns
            listofdataframes.append(df)
        else:
            print('{} has {} columns - skipping'.format(file,df.shape[1]))   
    bigdataframe = pd.concat(listofdataframes).reset_index(drop=True)
    bigdataframe.to_csv(outputcsv,index=False)
    




if __name__ == "__main__":

    app.run_server(debug=True, port=8888)