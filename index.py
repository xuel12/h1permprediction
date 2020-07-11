#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  4 17:31:03 2020

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
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash_extensions.callback import DashCallbackBlueprint

# from app import App, build_graph
from homepage import Homepage
from train import Training
from eda import EDA


import pandas as pd
import pickle



BASE_DIR = "/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/"
CODE_DIR = BASE_DIR+"h1permprediction/"
os.chdir(CODE_DIR)

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

    
dcb = DashCallbackBlueprint() 
    
# # Normally, Dash creates its own Flask server internally. By creating our own,
# # we can create a route for downloading files directly:
server = Flask(__name__)
    
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets=[dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])

app.config.suppress_callback_exceptions = True


@server.route(constants.DOWNLOAD_DIR + "<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(input_dir, path, as_attachment=True)


app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])


@app.callback(Output('page-content', 'children'),
            [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/training':
        return Training()
    elif pathname == '/eda':
        return EDA()
    else:
        return Homepage()
    

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
        header_dir = folderStruct(base_path)['header_dir']
        outputfile = 'h1b2015to2020.csv'
        headerfile = 'headers.csv'
        
        # read in csv to dataframe
        if count_newcsv > 0 or not os.path.exists(temp_dir + outputfile):
            csvCombine(input_dir, temp_dir, header_dir, outputfile, headerfile)
        
        makeEDAreports(outputfile, temp_dir)

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
    HEADER_DIR = BASE_PATH + 'header/'

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
    header_dir = HEADER_DIR
    if not os.path.exists(header_dir):
        os.makedirs(header_dir)


    return {'input_dir':input_dir, 'temp_dir':temp_dir, 'model_dir':model_dir,
            'download_dir':download_dir, 'BASE_PATH':BASE_PATH, 'CODE_DIR':CODE_DIR,
            'header_dir':header_dir} 


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
# def csvCombine(in_dir, temp_dir):
#     outputcsv = temp_dir+'bigcsv.csv' #specify filepath+filename of output csv
#     csv_path = in_dir

#     listofdataframes = []
#     for file in glob.glob(csv_path+'*.csv'):
#         df = pd.read_csv(file)
#         if df.shape[1] > 0: # make sure there are columns
#             listofdataframes.append(df)
#         else:
#             print('{} has {} columns - skipping'.format(file,df.shape[1]))   
#     bigdataframe = pd.concat(listofdataframes).reset_index(drop=True)
#     bigdataframe.to_csv(outputcsv,index=False)
    
def csvCombine(in_dir, temp_dir, header_dir, outputfile, headerfile):    
    # outputfile = temp_dir+outputfile    #specify filepath+filename of output csv

    # use header mapping file for parsing
    headers_df = pd.read_csv(header_dir+headerfile, index_col=0)

    # loop through all csv files in header file
    listofdataframes = []
    # csvfilenames = 'H-1B_Disclosure_Data_FY15_Q4'
    for csvfilenames in headers_df.to_dict().keys():
        csvfile = input_dir + csvfilenames + '.csv'
        if os.path.exists(csvfile):
            headers_temp = headers_df[csvfilenames]
            df = pd.read_csv(csvfile, usecols=headers_temp.dropna(),
                      dtype='str', 
                      parse_dates=[headers_temp['CASE_SUBMITTED']]).dropna(how='all')
            # filter rows, Remove "Withdraw" and "Certified Expired"
            df = df[((df['CASE_STATUS'].str.upper() == 'CERTIFIED') | \
                      (df['CASE_STATUS'].str.upper() == 'DENIED')) & \
                    (df['VISA_CLASS'].str.upper() == 'H-1B')]  
               
            # Similarly, most of employer come from the U.S.. We only keep application with American employer
            df = df[df.EMPLOYER_COUNTRY == 'UNITED STATES OF AMERICA']
     
            headers_temp_dict = {y:x for x,y in headers_temp.dropna().items()}
            df = df.rename(columns=headers_temp_dict)
            if df.shape[1] > 0: # make sure there are columns
                listofdataframes.append(df)
                print(csvfilenames + ' Done')
            else:
                print('{} has {} columns - skipping'.format(csvfilenames,df.shape[1]))
    df = pd.concat(listofdataframes).reset_index(drop=True)

    # uppercase all string for consistency  
    df = df.apply(lambda x: x.astype(str).str.upper())
    df['CASE_SUBMITTED'] = pd.to_datetime(df['CASE_SUBMITTED'])
    # df1 = df.fillna(value={'PREVAILING_WAGE': 0.0})
    # df2 = df1[df1["PREVAILING_WAGE"] == 'NAN']


    # mapping value based on mapping file    
    df['PW_WAGE_LEVEL'] = df['PW_WAGE_LEVEL'].replace(constants.PW_WAGE_LEVEL_MAP)
    df = df.replace({'PW_WAGE_LEVEL': constants.PW_WAGE_LEVEL_MAP, 
                        'EMPLOYER_STATE': constants.US_STATE_ABBREV,
                        'WORKSITE_STATE': constants.US_STATE_ABBREV,
                        "PREVAILING_WAGE": {'NAN': -1},
                        "PW_UNIT_OF_PAY": {'NAN': 'UNKNOWN'},
                        })
    df["PREVAILING_WAGE"] = pd.to_numeric(df["PREVAILING_WAGE"], downcast="float")
    df = df.replace({'NAN': 'UNKOWN'})

    # feature engineer on jobs
    df["EMPLOYER_NAME"]=df["EMPLOYER_NAME"].str.replace("INC.","INC")
    df['JOB_CATEGORY']=df['SOC_CODE'].apply(lambda x: jobClassifier(x))
    df['JOB_LEVEL']=df['JOB_TITLE'].apply(lambda x: levelClassifier(x))

    df.to_csv(temp_dir+outputfile, index=False)

    print('There are {} records.'.format(df.shape[0]))
    
    # return df


def jobClassifier(soc_code):
    soc_map = constants.SOC_MAP
    soc = str(soc_code).split('-')[0]        
    return soc_map.get(soc,'OTHER')


def levelClassifier(job_title):
    job_title = str(job_title)
    if job_title.find('SENIOR')!=-1 or job_title.find(' II')!=-1 or job_title.find('2')!=-1 or job_title.find('3')!=-1:
        return 'SENIOR'
    elif job_title.find('JUNIOR')!=-1 or job_title.find(' I')!=-1 or job_title.find('1')!=-1:
        return 'JUNIOR'
    else:
        return 'OTHER'
    
def makeEDAreports(csvfile, temp_dir):
    csvfile = 'h1b2015to2020_sub.csv'
    df = pd.read_csv(temp_dir + csvfile, parse_dates=['CASE_SUBMITTED'])

    edaplot = {}
    edaplot['EMPLOYER_STATE'] = df.groupby('EMPLOYER_STATE').count()
    edaplot['WORKSITE_STATE'] = df.groupby('WORKSITE_STATE').count()
    edaplot['JOB_CATEGORY'] = df.groupby('JOB_CATEGORY').count()
    edaplot['JOB_LEVEL'] = df.groupby('JOB_LEVEL').count()
    edaplot['FULL_TIME_POSITION'] = df.groupby('FULL_TIME_POSITION').count()
    edaplot['PW_WAGE_LEVEL'] = df.groupby('PW_WAGE_LEVEL').count()
    edaplot['H-1B_DEPENDENT'] = df.groupby('H-1B_DEPENDENT').count()
    edaplot['WILLFUL_VIOLATOR'] = df.groupby('WILLFUL_VIOLATOR').count()
    edaplot['CASE_SUBMITTED'] = (df.groupby(['CASE_STATUS', pd.Grouper(key='CASE_SUBMITTED', freq='M')])['JOB_CATEGORY']
        .count().reset_index().pivot(index='CASE_SUBMITTED', columns='CASE_STATUS', values='JOB_CATEGORY'))
    
               
    pickle_out = open(temp_dir+"eda.pickle","wb")
    pickle.dump(edaplot, pickle_out)
    pickle_out.close()

# @app.callback(
#     Output('output', 'children'),
#     [Input('pop_dropdown', 'value')]
# )
# def update_graph(city):
#     graph = build_graph(city)
#     return graph

if __name__ == '__main__':
    app.run_server(debug=True)
    
    