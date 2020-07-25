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
from train_perm import Training_perm
from eda import EDA
from eda_perm import EDA_perm

# from constants import JOB_LEVEL_MAP,US_STATE_ABBREV

import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression


BASE_DIR = "/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/"
# BASE_DIR = "/Users/42152/Desktop/"
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
input_dir_perm = constants.INPUT_DIR_PERM
if not os.path.exists(input_dir_perm):
    os.makedirs(input_dir_perm)

header_dir = constants.HEADER_DIR
if not os.path.exists(header_dir):
    os.makedirs(header_dir)
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
    elif pathname == '/training_perm':
        return Training_perm()
    elif pathname == '/eda':
        return EDA()
    elif pathname == '/eda_perm':
        return EDA_perm()
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
    Output("file-list-perm", "children"),
    [Input("upload-data-perm", "filename"), Input("upload-data-perm", "contents")],
)
def update_output_perm(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file_perm(name, data)
            # save_file(name, data)

    files = uploaded_files_perm()
    # files = uploaded_files()

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
    [Output('start-indicator-perm', 'color'), Output("submiting-data-perm", "children")],
    [Input("submit-data-perm", "n_clicks")])
def start_indicator_perm(n_clicks):
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
    Output('csvreader-status-perm', 'value'),
    # [Output("progress", "value"), Output("progress", "children")],
    # specify the component and its property that shall contain the output
    [Input('start-indicator-perm', 'color')],
    # specify the component and corresponding properties that shall serve as input
    [State('input-on-submit-perm','value')]) 
    # specify the component and corresponding properties that shall serve as input
def update_data_perm(color, base_path):  # define the function reaching output from input
    if color == 'blue':
        # BASE_PATH = value  # input value gives the base directory
        input_dir = folderStruct(base_path)['input_dir_perm']

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
    Output('xlsx2csv-indicator-perm', 'color'),
    # specify the component and its property that shall contain the output
    [Input('csvreader-status-perm', 'value')])
def xlsx2csv_indicator_perm(status):
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
        model_dir = folderStruct(base_path)['model_dir']

        outputfile = 'h1b2015to2020.csv'
        headerfile = 'headers.csv'
        
        # read in csv to dataframe
        if count_newcsv > 0 or not os.path.exists(temp_dir + outputfile):
            csvCombine(input_dir, temp_dir, header_dir, outputfile, headerfile)
        
        makeEDAreports(outputfile, temp_dir, model_dir)

        finish_message = 'Data parsing complete, find the parsed combineCSV in directory'
        # return progress, f"{progress} %" if progress >= 5 else ""
        return finish_message, 'done'
    else:
        return '', 'wait'


@app.callback(
    [Output('parsing-status-perm', 'children'), Output('combinecsv-status-perm', 'value')],
    # specify the component and its property that shall contain the output
    [Input('csvreader-status-perm', 'value')],
    [State('input-on-submit-perm','value')]) 
def update_combinedata_perm(count_newcsv, value):  # define the function reaching output from input
    if count_newcsv != -1:
        input_dir = folderStruct(base_path)['input_dir_perm']
        temp_dir = folderStruct(base_path)['temp_dir']
        header_dir = folderStruct(base_path)['header_dir']
        model_dir = folderStruct(base_path)['model_dir']
        outputfile = 'perm2015to2020.csv'
        headerfile = 'PERM_headers.csv'
        
        # read in csv to dataframe
        if count_newcsv > 0 or not os.path.exists(temp_dir + outputfile):
            csvCombine_perm(input_dir, temp_dir, header_dir, outputfile, headerfile)
        
        makeEDAreports_perm(outputfile, temp_dir, model_dir)

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
    Output('csvcombine-indicator-perm', 'color'),
    # specify the component and its property that shall contain the output
    [Input('combinecsv-status-perm', 'value')])
def csvcombine_indicator_perm(status):
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


@app.callback(
    [Output("progress-perm", "value"), Output("progress-perm", "children")],
    [Input('start-indicator-perm', 'color'),
      Input('xlsx2csv-indicator-perm', 'color'), Input('csvcombine-indicator-perm', 'color')],
)
def data_progress_perm(start_color, xlsx2csv_indicator, csvcombine_indicator):
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


def save_file_perm(filename, content):
    content_type, content_string = content.split(',')

    decoded = base64.b64decode(content_string)
    try:
        filename_csv = os.path.splitext(filename)[0]+'.csv'
        if not os.path.exists(input_dir_perm+filename_csv):
            if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif 'xlsx' in filename:
                # Assume that the user uploaded an excel file
                df = pd.read_excel(io.BytesIO(decoded))
            df.to_csv(input_dir_perm+filename_csv, index=False) 
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


def uploaded_files_perm():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(input_dir_perm):
        path = os.path.join(input_dir_perm, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = download_dir+"{}".format(urlquote(filename))
    return html.A(filename, href=location)

    
def folderStruct(BASE_DIR):
    CODE_DIR = BASE_DIR + "h1permprediction/"
    INPUT_DIR = BASE_DIR + "input_h1b/"
    # PREDICT_DIR = BASE_PATH + "predict/"
    TEMP_DIR = BASE_DIR + "temp/"
    INPUT_DIR_PERM = BASE_DIR + "input_perm/"
    # PREDICT_DIR = BASE_PATH + "predict/"
    # OUTPUT_DIR = BASE_PATH + "output/"
    DOWNLOAD_DIR = BASE_DIR + "download/"
    HEADER_DIR = CODE_DIR + 'header/'
    MODEL_DIR = CODE_DIR + "model/"

    os.chdir(CODE_DIR)
    # base_path = BASE_PATH
    input_dir = INPUT_DIR
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    temp_dir = TEMP_DIR
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    input_dir_perm = INPUT_DIR_PERM
    if not os.path.exists(input_dir_perm):
        os.makedirs(input_dir_perm)

    model_dir = MODEL_DIR
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    download_dir = DOWNLOAD_DIR
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    header_dir = HEADER_DIR
    if not os.path.exists(header_dir):
        os.makedirs(header_dir)


    return {'input_dir':input_dir, 'temp_dir':temp_dir, 
            'input_dir_perm':input_dir_perm,  
            'model_dir':model_dir,
            'download_dir':download_dir, 'BASE_PATH':BASE_DIR, 'CODE_DIR':CODE_DIR,
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
                
    
def csvCombine(input_dir, temp_dir, header_dir, outputfile, headerfile):
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
                        "PW_UNIT_OF_PAY": constants.UNIT_MAP,
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

def csvCombine_perm(input_dir, temp_dir, header_dir, outputfile, headerfile):

    headers_df = pd.read_csv(header_dir + headerfile, index_col=0)

    # loop through all csv files in header file
    listofdataframes = []
    # csvfilenames = 'H-1B_Disclosure_Data_FY15_Q4'
    for csvfilenames in headers_df.to_dict().keys():
        csvfile = input_dir + csvfilenames + '.csv'
        if os.path.exists(csvfile):
            headers_temp = headers_df[csvfilenames]
            df = pd.read_csv(csvfile, usecols=headers_temp.dropna(),
                      dtype='str', 
                      parse_dates=[headers_temp['CASE_RECEIVED_DATE']]).dropna(how='all')
            # filter rows, Remove "Withdraw" and "Certified Expired"
            df = df[((df['CASE_STATUS'].str.upper() == 'CERTIFIED') | \
                      (df['CASE_STATUS'].str.upper() == 'DENIED'))]
            df = df.replace({'WORKSITE_STATE': constants.US_STATE_ABBREV,
                             'JOB_INFO_WORK_STATE': constants.US_STATE_ABBREV,
                    })
            df = df.fillna('UNKOWN')
   
            # # Similarly, most of employer come from the U.S.. We only keep application with American employer
            # df = df[df.EMPLOYER_COUNTRY == 'UNITED STATES OF AMERICA']
     
            headers_temp_dict = {y:x for x,y in headers_temp.dropna().items()}
            df = df.rename(columns=headers_temp_dict)
            if df.shape[1] > 0: # make sure there are columns
                listofdataframes.append(df)
                print(csvfilenames + ' Done')
            else:
                print('{} has {} columns - skipping'.format(csvfilenames,df.shape[1]))
    df = pd.concat(listofdataframes).reset_index(drop=True)
    
    df.to_csv(temp_dir + outputfile, index=False)
    print('There are {} records.'.format(df.shape[0]))


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
    
    
def makeEDAreports(csvfile, temp_dir, model_dir):
    csvfile = 'h1b2015to2020.csv'
    df = pd.read_csv(temp_dir + csvfile, parse_dates=['CASE_SUBMITTED'])
    df["PW_WAGE_LEVEL"] = df["PW_WAGE_LEVEL"].map(constants.JOB_LEVEL_MAP)
    df = df.replace('UNKOWN','UNKNOWN')
    df['countvar'] = 1


    edaplot = {}
    edaplot['CASE_STATUS'] = df.groupby('CASE_STATUS').count()
    edaplot['EMPLOYER_STATE'] = df.groupby('EMPLOYER_STATE').count()
    edaplot['WORKSITE_STATE'] = df.groupby('WORKSITE_STATE').count()
    edaplot['JOB_CATEGORY'] = df.groupby('JOB_CATEGORY').count().sort_values(['countvar'], ascending=False)[0:10]
    edaplot['JOB_LEVEL'] = df.groupby(['JOB_LEVEL','CASE_STATUS'],as_index=False).count()
    edaplot['FULL_TIME_POSITION'] = df.groupby('FULL_TIME_POSITION').count()
    edaplot['PW_WAGE_LEVEL'] = df.groupby(['PW_WAGE_LEVEL','CASE_STATUS'],as_index=False).count()
    edaplot['H-1B_DEPENDENT'] = df.groupby(['H-1B_DEPENDENT','CASE_STATUS'],as_index=False).count()
    edaplot['WILLFUL_VIOLATOR'] = df.groupby('WILLFUL_VIOLATOR').count()
    edaplot['CASE_SUBMITTED'] = (df.groupby(['CASE_STATUS', pd.Grouper(key='CASE_SUBMITTED', freq='M')])['JOB_CATEGORY']
        .count().reset_index().pivot(index='CASE_SUBMITTED', columns='CASE_STATUS', values='JOB_CATEGORY'))
    
               
    pickle_out = open(model_dir+"eda.pickle","wb")
    pickle.dump(edaplot, pickle_out)
    pickle_out.close()


def makeEDAreports_perm(csvfile, temp_dir, model_dir):
    csvfile = 'perm2015to2020.csv'
    perm = pd.read_csv(temp_dir + csvfile, parse_dates=['CASE_RECEIVED_DATE'])
    perm = perm.fillna("Unknown")
    perm["JOB_INFO_WORK_STATE"] = perm["JOB_INFO_WORK_STATE"].map(constants.US_STATE_ABBREV)
    perm["EMPLOYER_STATE"] = perm["EMPLOYER_STATE"].map(constants.US_STATE_ABBREV)
    perm['countvar'] = 1
    perm = perm.replace('Certified', 'CERTIFIED')
    perm = perm.replace('Denied', 'DENIED')

    edaplot = {}
    edaplot['CASE_STATUS'] = perm.groupby('CASE_STATUS').count()
    edaplot['EMPLOYER_STATE'] = perm.groupby('EMPLOYER_STATE').count()
    edaplot['WORKSITE_STATE'] = perm.groupby('JOB_INFO_WORK_STATE').count()
    edaplot['PW_WAGE_LEVEL'] = perm.groupby(['PW_LEVEL_9089','CASE_STATUS'],as_index=False).count()
    edaplot['REFILE'] = perm.groupby(['REFILE','CASE_STATUS'],as_index=False).count()
    edaplot['EDUCATION'] = perm.groupby(['FOREIGN_WORKER_INFO_EDUCATION', 'CASE_STATUS'], as_index=False).count()
    edaplot['JOB_INFO_ALT_FIELD'] = perm.groupby(['JOB_INFO_ALT_FIELD', 'CASE_STATUS'], as_index=False).count()
    dftop = perm.groupby('FW_INFO_BIRTH_COUNTRY', as_index=False).count()
    dftop = dftop.sort_values('countvar', ascending=False)[['FW_INFO_BIRTH_COUNTRY', 'countvar']][0:6]
    edaplot['FW_INFO_BIRTH_COUNTRY'] = perm.groupby(['FW_INFO_BIRTH_COUNTRY', 'CASE_STATUS'], as_index=False).count()
    edaplot['FW_INFO_BIRTH_COUNTRY'] = edaplot['FW_INFO_BIRTH_COUNTRY'][edaplot['FW_INFO_BIRTH_COUNTRY'].FW_INFO_BIRTH_COUNTRY.isin(dftop.FW_INFO_BIRTH_COUNTRY)]
    dftop2 = perm.groupby('CLASS_OF_ADMISSION', as_index=False).count()
    dftop2 = dftop2.sort_values('countvar', ascending=False)[['CLASS_OF_ADMISSION', 'countvar']][0:6]
    edaplot['CLASS_OF_ADMISSION'] = perm.groupby(['CLASS_OF_ADMISSION', 'CASE_STATUS'], as_index=False).count()
    edaplot['CLASS_OF_ADMISSION'] = edaplot['CLASS_OF_ADMISSION'][edaplot['CLASS_OF_ADMISSION'].CLASS_OF_ADMISSION.isin(dftop2.CLASS_OF_ADMISSION)]
    edaplot['FW_INFO_TRAINING_COMP'] = perm.groupby(['FW_INFO_TRAINING_COMP', 'CASE_STATUS'], as_index=False).count()
    edaplot['JOB_INFO_JOB_REQ_NORMAL'] = perm.groupby(['JOB_INFO_JOB_REQ_NORMAL', 'CASE_STATUS'], as_index=False).count()
    edaplot['CASE_RECEIVED_DATE'] = (perm.groupby(['CASE_STATUS', pd.Grouper(key='CASE_RECEIVED_DATE', freq='M')])['JOB_INFO_WORK_STATE']
        .count().reset_index().pivot(index='CASE_RECEIVED_DATE', columns='CASE_STATUS', values='JOB_INFO_WORK_STATE'))

    pickle_out = open(model_dir + "edaPERM.pickle", "wb")
    pickle.dump(edaplot, pickle_out)
    pickle_out.close()


# h1b prediction
@app.callback(
    [Output("my-output", "children"), Output('predict-indicator', 'color'), 
     Output("submitting-predict", "children")],
    [Input("submit-predict", "n_clicks"), Input("MODEL_dropdown", "value"),
     Input("EMPLOYER_STATE_dropdown", "value"),
        Input("WORKSITE_STATE_dropdown", "value"),
        Input("JOB_CATEGORY_dropdown", "value"),
        Input("JOB_LEVEL_dropdown", "value"),
        Input("FULL_TIME_POSITION_dropdown", "value"),
        Input("PW_UNIT_OF_PAY_dropdown", "value"),
        Input("PW_WAGE_LEVEL_dropdown", "value"),
        Input("H-1B_DEPENDENT_dropdown", "value"),
        Input("WILLFUL_VIOLATOR_dropdown", "value")
    ])
def predict_h1b(n_clicks, modelchoice, employer_state, worksite_state, job_category, job_level, 
                      fulltime_position, wage_unit, wage_level, dependent, violator):
    model_dir = folderStruct(base_path)['model_dir']

    # input_dict = {
    #     "employer_state": employer_state,
    #     "worksite_state": worksite_state,
    #     "job_category": job_category,
    #     "job_level": job_level,
    #     "fulltime_position":fulltime_position,
    #     "wage_unit":wage_unit,
    #     "wage_level":wage_level,
    #     "dependent":dependent,
    #     "violator":violator,
    # }

    if modelchoice == 'Pre-trained':
        model_filename = 'H1B_LR_MODEL_2020.pickle'
        color = 'red'
    else:
        model_filename = 'H1B_USER_MODEL.pickle'
        color = 'blue'


    with open(model_dir + model_filename, 'rb') as file:  
        model = pickle.load(file)
    

    if n_clicks % 2 == 1:
        time.sleep(1)
        progress = 'Done'
        result = model.predict(np.array([[0]*151]))[0]
    else:
        progress = 'Standby'
        result = ''


    # data20 = df[cate_column_name].iloc[:100,].copy()
    # data20 = pd.get_dummies(data20, columns=cate_column_name)
    # data20 = data20.reset_index(drop=True)
    return 'Prediction result: {}'.format(result), color, progress




@app.callback(
    Output("train-indicator", "color"), 
    [Input("submit-training", "n_clicks")]
    )
def UsertrainH1B(n_clicks):
    temp_dir = folderStruct(base_path)['temp_dir']
    model_dir = folderStruct(base_path)['model_dir']

    if n_clicks % 2 == 1:
        df = pd.read_csv(temp_dir+'h1b2015to2020_sub.csv', engine = 'python')
        # df["PW_UNIT_OF_PAY"] = df["PW_UNIT_OF_PAY"].replace(constants.UNIT_MAP)

        df = df[constants.H1B_TRAIN_FEATURES]

        data = pd.get_dummies(df, columns=constants.H1B_CATEG_FEATURES)
        data = data.reset_index(drop=True)
        X_train = data.drop(['CASE_STATUS'], axis=1)
        y_train = data['CASE_STATUS']
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
    
        pickle_out = open(model_dir + "H1B_USER_MODEL.pickle", "wb")
        pickle.dump(model, pickle_out)
        pickle_out.close()
        color = 'blue'
    else:
        color = 'grey'
    return color
    

@app.callback(
    Output("train-indicator-perm", "color"), 
    [Input("submit-training-perm", "n_clicks")]
    )
def UsertrainPERM(n_clicks):
    temp_dir = folderStruct(base_path)['temp_dir']
    model_dir = folderStruct(base_path)['model_dir']

    if n_clicks % 2 == 1:
        df = pd.read_csv(temp_dir+'perm2015to2019_sub.csv', engine = 'python')

        df = df[constants.PERM_TRAIN_FEATURES]

        data = pd.get_dummies(df, columns=constants.PERM_CATEG_FEATURES)
        data = data.reset_index(drop=True)
        
        X_train = data.drop(['CASE_STATUS'], axis=1)
        y_train = data['CASE_STATUS']

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
    
        pickle_out = open(model_dir + "PERM_USER_MODEL.pickle", "wb")
        pickle.dump(model, pickle_out)
        pickle_out.close()
        color = 'blue'
    else:
        color = 'grey'
    return color



if __name__ == '__main__':
    app.run_server(debug=True)
    
    