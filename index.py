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
# from urllib.parse import quote as urlquote
import subprocess
from datetime import datetime as dt

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
from userguide import userGuide, buildModel, h1bModel, permModel, aboutEDA, contactus, documents

import pandas as pd
import pickle
from sklearn.linear_model import LogisticRegression
# from sklearn.ensemble import RandomForestClassifier
# from imblearn.over_sampling import SMOTE

os.chdir(os.getcwd())

import constants

# initial directory
base_path = os.getcwd() + '/../'
    
dcb = DashCallbackBlueprint() 
    
# Normally, Dash creates its own Flask server internally. By creating our own, we can create a route for downloading files directly:
server = Flask(__name__)
    
external_stylesheets=[dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True


# downloading host
@server.route(base_path + "<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(base_path, path, as_attachment=True)


app.layout = html.Div([
    dcc.Location(id = 'url', refresh = False),
    html.Div(id = 'page-content')
])


# page layout
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
    elif pathname == '/userguide':
        return userGuide()
    elif pathname == '/buildmodel':
        return buildModel()
    elif pathname == '/h1bmodel':
        return h1bModel()
    elif pathname == '/permmodel':
        return permModel()
    elif pathname == '/aboutEDA':
        return aboutEDA()
    elif pathname == '/contactus':
        return contactus()
    elif pathname == '/documents':
        return documents()
    else:
        return Homepage()
    

# create file list H1B
def uploaded_files(input_dir):
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(input_dir):
        path = os.path.join(input_dir, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


# create file list PERM
def uploaded_files_perm(input_dir_perm):
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(input_dir_perm):
        path = os.path.join(input_dir_perm, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


# visualize list of files
def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    # location = download_dir+"{}".format(urlquote(filename))
    # return html.A(filename, href=location)
    return html.A(filename)


# list of input files H1B
@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents"), 
     Input('input-on-submit','value')])
def update_output(uploaded_filenames, uploaded_file_contents, base_path):
    """Save uploaded files and regenerate the file list."""
    input_dir = folderStruct(base_path)['input_dir']

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data, input_dir)

    files = uploaded_files(input_dir)
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]
    

# list of input files PERM
@app.callback(
    Output("file-list-perm", "children"),
    [Input("upload-data-perm", "filename"), Input("upload-data-perm", "contents"),
     Input('input-on-submit-perm','value')])
def update_output_perm(uploaded_filenames, uploaded_file_contents, base_path):
    """Save uploaded files and regenerate the file list."""
    input_dir_perm = folderStruct(base_path)['input_dir_perm']

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file_perm(name, data, input_dir_perm)

    files = uploaded_files_perm(input_dir_perm)

    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]
    
    
# preprocessing start indicator H1B
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


# preprocessing start indicator PERM
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


# update input files H1B
@app.callback(
    Output('csvreader-status', 'value'),
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
        return count_newcsv
    else:
        return -1


# update input files PERM
@app.callback(
    Output('csvreader-status-perm', 'value'),
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
        return count_newcsv
    else:
        return -1
    
    
# indicator for csv parsing status H1B
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


# indicator for csv parsing status PERM
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


# indicator for preprocess status H1B
@app.callback(
    [Output('parsing status', 'children'), Output('combinecsv-status', 'value')],
    # specify the component and its property that shall contain the output
    [Input('csvreader-status', 'value')],
    [State('input-on-submit','value')]) 
def update_combinedata(count_newcsv, base_path):  # define the function reaching output from input
    if count_newcsv != -1:
        temp_dir = folderStruct(base_path)['temp_dir']
        input_dir = folderStruct(base_path)['input_dir']
        # header_dir = folderStruct(base_path)['header_dir']
        # model_dir = folderStruct(base_path)['model_dir']
        model_dir = constants.MODEL_DIR
        header_dir = constants.HEADER_DIR()
        
        outputfile = 'h1b2015to2020.csv'
        headerfile = 'headers.csv'
        
        # read in csv to dataframe
        if count_newcsv > 0 or not os.path.exists(temp_dir + outputfile):
            csvCombine(input_dir, temp_dir, header_dir, outputfile, headerfile)
        
        makeEDAreports(outputfile, temp_dir, model_dir)

        finish_message = 'Data parsing complete, find the parsed combineCSV in directory'
        return finish_message, 'done'
    else:
        return '', 'wait'


# indicator for preprocess status PERM
@app.callback(
    [Output('parsing-status-perm', 'children'), Output('combinecsv-status-perm', 'value')],
    # specify the component and its property that shall contain the output
    [Input('csvreader-status-perm', 'value')],
    [State('input-on-submit-perm','value')]) 
def update_combinedata_perm(count_newcsv, base_path):  # define the function reaching output from input
    if count_newcsv != -1:
        input_dir = folderStruct(base_path)['input_dir_perm']
        temp_dir = folderStruct(base_path)['temp_dir']
        # header_dir = folderStruct(base_path)['header_dir']
        # model_dir = folderStruct(base_path)['model_dir']
        model_dir = constants.MODEL_DIR
        header_dir = constants.HEADER_DIR()

        outputfile = 'perm2015to2020.csv'
        headerfile = 'PERM_headers.csv'
        
        # read in csv to dataframe
        if count_newcsv > 0 or not os.path.exists(temp_dir + outputfile):
            csvCombine_perm(input_dir, temp_dir, header_dir, outputfile, headerfile)
        
        makeEDAreports_perm(outputfile, temp_dir, model_dir)

        finish_message = 'Data parsing complete, find the parsed combineCSV in directory'
        return finish_message, 'done'
    else:
        return '', 'wait'
    
    
# indicator for ending preprocess H1B
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
    
 
# indicator for ending preprocess PERM
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


# progress bar for H1B preprocessing
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


# progress bar for PERM preprocessing
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


# transform xlsx into csv for faster process H1B
def save_file(filename, content, input_dir):
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


# transform xlsx into csv for faster process PERM
def save_file_perm(filename, content, input_dir_perm):
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
    

# dynamically change folder based on user input   
def folderStruct(BASE_DIR):
    CODE_DIR = BASE_DIR + "h1permprediction/"
    INPUT_DIR = BASE_DIR + "input_h1b/"
    TEMP_DIR = BASE_DIR + "temp/"
    INPUT_DIR_PERM = BASE_DIR + "input_perm/"
    DOWNLOAD_DIR = BASE_DIR + "download/"
    HEADER_DIR = CODE_DIR + 'header/'
    MODEL_DIR = CODE_DIR + "model/"

    # os.chdir(CODE_DIR)
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
                

# combine datasets into one file for H1B    
def csvCombine(input_dir, temp_dir, header_dir, outputfile, headerfile):
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

    # mapping value based on mapping file    
    df['PW_WAGE_LEVEL'] = df['PW_WAGE_LEVEL'].replace(constants.PW_WAGE_LEVEL_MAP)
    df = df.replace({'PW_WAGE_LEVEL': constants.PW_WAGE_LEVEL_MAP, 
                        'EMPLOYER_STATE': constants.US_STATE_ABBREV,
                        'WORKSITE_STATE': constants.US_STATE_ABBREV,
                        "PREVAILING_WAGE": {'NAN': -1},
                        "PW_UNIT_OF_PAY": constants.UNIT_MAP,
                        })
    df["PREVAILING_WAGE"] = pd.to_numeric(df["PREVAILING_WAGE"], downcast="float")
    df = df.replace({'NAN': 'UNKNOWN'})

    # feature engineer on jobs
    df["EMPLOYER_NAME"]=df["EMPLOYER_NAME"].str.replace("INC.","INC")
    df['JOB_CATEGORY']=df['SOC_CODE'].apply(lambda x: jobClassifier(x))
    df['JOB_LEVEL']=df['JOB_TITLE'].apply(lambda x: levelClassifier(x))

    df.to_csv(temp_dir+outputfile, index=False)
    print('There are {} records.'.format(df.shape[0]))
    

# combine datasets into one file for PERM
def csvCombine_perm(input_dir, temp_dir, header_dir, outputfile, headerfile):

    headers_df = pd.read_csv(header_dir + headerfile, index_col=0)

    # loop through all csv files in header file
    listofdataframes = []
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
    
    # uppercase all string for consistency  
    df = df.apply(lambda x: x.astype(str).str.upper())
    df['CASE_RECEIVED_DATE'] = pd.to_datetime(df['CASE_RECEIVED_DATE'])
    # filter only cases later than 2015
    df = df.loc[df['CASE_RECEIVED_DATE'] >= '2015-01-01']
    
    df = df.replace({'WORKSITE_STATE': constants.US_STATE_ABBREV,
                     'JOB_INFO_WORK_STATE': constants.US_STATE_ABBREV,
                     'EMPLOYER_STATE': constants.US_STATE_ABBREV,
                    })
    df = df.fillna('UNKNOWN')
    df = df.replace({'NAN': 'UNKNOWN'})

    df.to_csv(temp_dir + outputfile, index=False)
    print('There are {} records.'.format(df.shape[0]))


# function to translate SOC code in job category
def jobClassifier(soc_code):
    soc_map = constants.SOC_MAP
    soc = str(soc_code).split('-')[0]        
    return soc_map.get(soc,'OTHER')


# function to translate Job level
def levelClassifier(job_title):
    job_title = str(job_title)
    if job_title.find('SENIOR')!=-1 or job_title.find(' II')!=-1 or job_title.find('2')!=-1 or job_title.find('3')!=-1:
        return 'SENIOR'
    elif job_title.find('JUNIOR')!=-1 or job_title.find(' I')!=-1 or job_title.find('1')!=-1:
        return 'JUNIOR'
    else:
        return 'OTHER'
    
    
# create EDA report for H1B
def makeEDAreports(csvfile, temp_dir, model_dir):
    csvfile = 'h1b2015to2020.csv'
    df = pd.read_csv(temp_dir + csvfile, parse_dates=['CASE_SUBMITTED'])
    df["PW_WAGE_LEVEL"] = df["PW_WAGE_LEVEL"].map(constants.JOB_LEVEL_MAP)
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


# create EDA report for PERM
def makeEDAreports_perm(csvfile, temp_dir, model_dir):
    csvfile = 'perm2015to2020.csv'
    perm = pd.read_csv(temp_dir + csvfile, parse_dates=['CASE_RECEIVED_DATE'])
    perm['countvar'] = 1


    edaplot = {}
    edaplot['CASE_STATUS'] = perm.groupby('CASE_STATUS').count()
    edaplot['FW_OWNERSHIP_INTEREST'] = perm.groupby('FW_OWNERSHIP_INTEREST').count()
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
        Input("WILLFUL_VIOLATOR_dropdown", "value")])
def predict_h1b(n_clicks, modelchoice, employer_state, worksite_state, job_category, job_level, 
                      fulltime_position, wage_unit, wage_level, dependent, violator):
    # model_dir = folderStruct(base_path)['model_dir']
    model_dir = constants.MODEL_DIR

    input_dict = {
        "EMPLOYER_STATE": [employer_state],
        "WORKSITE_STATE": [worksite_state],
        "JOB_CATEGORY": [job_category],
        "JOB_LEVEL": [job_level],
        "FULL_TIME_POSITION":[fulltime_position],
        "PW_UNIT_OF_PAY":[wage_unit],
        "PW_WAGE_LEVEL":[wage_level],
        "H-1B_DEPENDENT":[dependent],
        "WILLFUL_VIOLATOR":[violator],
    }
    
    if modelchoice == 'Pre-trained':
        model_filename = 'H1B_LR_MODEL_2020.pickle'
        col_file = 'H1B_LR_MODEL_2020_COL.pickle'
        color = 'red'
    else:
        model_filename = 'H1B_USER_MODEL.pickle'
        col_file = 'H1B_USER_MODEL_COL.pickle'
        color = 'blue'

    with open(model_dir + model_filename, 'rb') as file:  
        model = pickle.load(file)
    with open(model_dir + col_file, 'rb') as file:  
        col_sample = pickle.load(file)  


    df = pd.DataFrame.from_dict(input_dict)
    print(df)
    
    data = pd.get_dummies(df)
    missing_cols = set(col_sample.columns) - set(data.columns)
    # Add a missing column in user info with default value equal to 0
    for c in missing_cols:
        data[c] = 0
    
    # Ensure the order of column in the user info is in the same order than in train set
    data = data[col_sample.columns]
    
    if n_clicks % 2 == 1:
        time.sleep(1)
        progress = 'Done'
        result, prob = [model.predict(data)[0], model.predict_proba(data)[0][0]]
    else:
        progress = 'Standby'
        result, prob = ['Not available','Not available']

    return 'Prediction result: {}, Certified probability is {}'.format(result, prob), color, progress


# perm prediction
@app.callback(
    [Output("my-output-perm", "children"), Output('predict-indicator-perm', 'color'), 
     Output("submitting-predict-perm", "children")],
    [Input("submit-predict-perm", "n_clicks"), 
     Input("PERM_MODEL_dropdown", "value"),
     Input("PERM_WORKSITE_STATE_dropdown", "value"),
     Input("PERM_REFILE_dropdown", "value"),
     Input("PERM_FW_OWNERSHIP_INTEREST_dropdown", "value"),
     Input("PERM_PW_LEVEL_9089_dropdown", "value"),
     Input("PERM_JOB_INFO_EDUCATION_dropdown", "value"),
     Input("PERM_JOB_INFO_TRAINING_dropdown", "value"),
     Input("PERM_JOB_INFO_ALT_FIELD_dropdown", "value"),
     Input("PERM_JOB_INFO_JOB_REQ_NORMAL_dropdown", "value"),
     Input("PERM_JOB_INFO_FOREIGN_LANG_REQ_dropdown", "value"),
     Input("PERM_RECR_INFO_PROFESSIONAL_OCC_dropdown", "value"),
     Input("PERM_RECR_INFO_COLL_UNIV_TEACHER_dropdown", "value"),
     Input("PERM_FW_INFO_BIRTH_COUNTRY_dropdown", "value"),
     Input("PERM_CLASS_OF_ADMISSION_dropdown", "value"),
     Input("PERM_FW_INFO_TRAINING_COMP_dropdown", "value")])
def predict_perm(n_clicks, modelchoice, worksite_state, refile, ownership, skill_level,
                      education, training_required, alt_field, require_normal, foregin_language,
                      professional, college_teacher, birthcountry, visa_class, training_complete):
    # model_dir = folderStruct(base_path)['model_dir']
    model_dir = constants.MODEL_DIR

    input_dict = {
        "WORKSITE_STATE": [worksite_state],
        "REFILE": [refile],
        "FW_OWNERSHIP_INTEREST": [ownership],
        "PW_LEVEL_9089": [skill_level],
        "JOB_INFO_EDUCATION":[education],
        "JOB_INFO_TRAINING":[training_required],
        "JOB_INFO_ALT_FIELD":[alt_field],
        "JOB_INFO_JOB_REQ_NORMAL":[require_normal],
        "JOB_INFO_FOREIGN_LANG_REQ":[foregin_language],
        "RECR_INFO_PROFESSIONAL_OCC":[professional],
        "RECR_INFO_COLL_UNIV_TEACHER":[college_teacher],
        "FW_INFO_BIRTH_COUNTRY":[birthcountry],
        "CLASS_OF_ADMISSION":[visa_class],
        "FW_INFO_TRAINING_COMP":[training_complete],
    }

    
    if modelchoice == 'Pre-trained':
        model_filename = 'PERM_RF_MODEL_2020.pickle'
        col_file = 'PERM_RF_MODEL_2020_COL.pickle'
        color = 'red'
    else:
        model_filename = 'PERM_USER_MODEL.pickle'
        col_file = 'PERM_USER_MODEL_COL.pickle'
        color = 'blue'

    with open(model_dir + model_filename, 'rb') as file:  
        model = pickle.load(file)
    with open(model_dir + col_file, 'rb') as file:  
        col_sample = pickle.load(file)  


    df = pd.DataFrame.from_dict(input_dict)
    
    data = pd.get_dummies(df)
    missing_cols = set(col_sample.columns) - set(data.columns)
    # Add a missing column in user info with default value equal to 0
    for c in missing_cols:
        data[c] = 0
    
    # Ensure the order of column in the user info is in the same order than in train set
    data = data[col_sample.columns]
    
    if n_clicks % 2 == 1:
        time.sleep(1)
        progress = 'Done'
        # result = model.predict(np.array([[0]*151]))[0]
        result, prob = [model.predict(data)[0], model.predict_proba(data)[0][0]]
    else:
        progress = 'Standby'
        result, prob = ['Not available','Not available']

    return 'Prediction result: {}, Certified probability is {}'.format(result, prob), color, progress


# training procedure on H1B
@app.callback(
    Output("train-indicator", "color"), 
    [Input("submit-training", "n_clicks"),
     Input('h1b-date-picker-range', 'start_date'),
     Input('h1b-date-picker-range', 'end_date')],
    [State('input-on-submit','value')]) 
def UsertrainH1B(n_clicks, start_date, end_date, base_path):
    temp_dir = folderStruct(base_path)['temp_dir']
    # model_dir = folderStruct(base_path)['model_dir']
    model_dir = constants.MODEL_DIR
        
    if n_clicks % 2 == 1:
        df = pd.read_csv(temp_dir+'h1b2015to2020.csv', parse_dates=['CASE_SUBMITTED'])

        # filter only cases between select range
        if start_date is not None:
            start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        else:
            start_date = df['CASE_SUBMITTED'].min()
        if end_date is not None:
            end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        else:
            end_date = df['CASE_SUBMITTED'].max()
        df = df.loc[(df['CASE_SUBMITTED'] >= start_date) & (df['CASE_SUBMITTED'] <= end_date)]

        # select features for training        
        df = df[constants.H1B_TRAIN_FEATURES]

        data = pd.get_dummies(df, columns=constants.H1B_CATEG_FEATURES)
        data = data.reset_index(drop=True)
        
        X_train = data.drop(['CASE_STATUS'], axis=1)
        y_train = data['CASE_STATUS']
        COLsample = X_train.head(1)

        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
    
        pickle_out = open(model_dir + "H1B_USER_MODEL.pickle", "wb")
        pickle.dump(model, pickle_out)
        pickle_out.close()
        
        pickle_out2 = open(model_dir + "H1B_USER_MODEL_COL.pickle", "wb")
        pickle.dump(COLsample, pickle_out2)
        pickle_out2.close()
    
        color = 'blue'
    else:
        color = 'grey'
    return color
    
# training procedure on PERM
@app.callback(
    Output("train-indicator-perm", "color"), 
    [Input("submit-training-perm", "n_clicks"),
     Input('perm-date-picker-range', 'start_date'),
     Input('perm-date-picker-range', 'end_date')],
    [State('input-on-submit-perm','value')]) 
def UsertrainPERM(n_clicks, start_date, end_date, base_path):
    temp_dir = folderStruct(base_path)['temp_dir']
    # model_dir = folderStruct(base_path)['model_dir']
    model_dir = constants.MODEL_DIR

    if n_clicks % 2 == 1:
        df = pd.read_csv(temp_dir+'perm2015to2020.csv', parse_dates=['CASE_RECEIVED_DATE'])

        # filter only cases between select range
        if start_date is not None:
            start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        else:
            start_date = df['CASE_RECEIVED_DATE'].min()
        if end_date is not None:
            end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        else:
            end_date = df['CASE_RECEIVED_DATE'].max()
        df = df.loc[(df['CASE_RECEIVED_DATE'] >= start_date) & (df['CASE_RECEIVED_DATE'] <= end_date)]
        
        df = df[constants.PERM_TRAIN_FEATURES]

        data = pd.get_dummies(df, columns=constants.PERM_CATEG_FEATURES)
        data = data.reset_index(drop=True)
        
        X_train = data.drop(['CASE_STATUS'], axis=1)
        y_train = data['CASE_STATUS']
        COLsample = X_train.head(1)

        # # SMOTE with random forest
        # oversample = SMOTE()
        # x_train_n, y_train_n = oversample.fit_resample(X_train, y_train)
        # model = RandomForestClassifier(n_estimators=100, bootstrap=True, criterion='gini', oob_score=True)
        # model.fit(x_train_n, y_train_n)
    
        model = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
    
        pickle_out = open(model_dir + "PERM_USER_MODEL.pickle", "wb")
        pickle.dump(model, pickle_out)
        pickle_out.close()
        
        pickle_out2 = open(model_dir + "PERM_USER_MODEL_COL.pickle", "wb")
        pickle.dump(COLsample, pickle_out2)
        pickle_out2.close()
        
        color = 'blue'
    else:
        color = 'grey'
    return color



if __name__ == '__main__':
    app.run_server(debug=True)
    
    