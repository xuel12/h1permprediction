#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 19 22:12:01 2020

@author: xuel12
"""

# import numpy as np
import pandas as pd
import os
import sys
import glob
import re
import subprocess
import time

# import xlrd
# import csv
    
import plotly
# import getpass
import plotly.graph_objs as go
# import plotly.express as xp
# from plotly.offline import iplot
# import datetime
# from sklearn.preprocessing import StandardScaler
# from sklearn.naive_bayes import MultinomialNB
# from sklearn.naive_bayes import GaussianNB
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score,confusion_matrix,roc_auc_score
# from sklearn.ensemble import RandomForestClassifier
# from imblearn.over_sampling import SMOTE

try: 
    os.chdir('/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/h1permprediction')
    print("Current directory is {}".format(os.getcwd()))
except: 
    print("Something wrong with specified directory. Exception- ", sys.exc_info())
    
import constants

    
# convert xlsx to csv
def xlsx2csv(in_dir):
    xlsx_path = in_dir
    csv_path = in_dir
    list_of_xlsx = glob.glob(xlsx_path+'*.xlsx')
            
    for xlsx in list_of_xlsx:
        # Extract File Name on group 2 "(.+)"
        filename = re.search(r'(.+[\\|\/])(.+)(\.(xlsx))', xlsx).group(2)
        if not os.path.exists(csv_path+filename+'.csv'):
            # with xlrd.open_workbook(xlsx_path+filename+'.xlsx') as wb:
            #     sh = wb.sheet_by_index(0)  # or wb.sheet_by_name('name_of_the_sheet_here')
            #     with open(csv_path+filename+'.csv', 'w') as f:   # open('a_file.csv', 'w', newline="") for python 3
            #         c = csv.writer(f)
            #         for r in range(sh.nrows):
            #             c.writerow(sh.row_values(r))
                
            # Setup the call for subprocess.call()
            call = ["python", "./xlsx2csv.py", xlsx, csv_path+filename+'.csv']
            try:
                subprocess.call(call) # On Windows use shell=True
            except:
                print('Failed with {}'.format(xlsx_path))


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
    
    

# def cleanupH1B19(H1B19_csvfile):
#     col_types = constants.COL_TYPES
#     parse_dates = constants.PARSE_DATES
    
#     H1B19 = pd.read_csv(H1B19_csvfile, 
#                         # header=None, names=headers, 
#                         dtype=col_types, parse_dates=parse_dates,low_memory=True).dropna(how='all')
    
#     # keep certain columns for analysis
#     headers = constants.HEADERS
#     H1B19 = H1B19[headers]

#     # miss labeling the header in the original table
#     H1B19 = H1B19.rename(columns={"NAME_OF_HIGHEST_STATE_COURT": "STATE_OF_HIGHEST_COURT"})
#     # filter H1B rows, Remove "Withdraw" and "Certified Expired"
#     H1B19 = H1B19[((H1B19['CASE_STATUS'].str.upper() == 'CERTIFIED') | \
#                                (H1B19['CASE_STATUS'].str.upper() == 'DENIED')) & \
#                               (H1B19['VISA_CLASS'].str.upper() == 'H-1B')]  
#     # Similarly, most of employer come from the U.S.. We only keep application with American employer
#     H1B19 = H1B19[H1B19.EMPLOYER_COUNTRY == 'UNITED STATES OF AMERICA']
#     print('There are {} records.'.format(H1B19.shape[0]))

#     # dateformat standardization
#     for datecol in parse_dates:
#         H1B19[datecol] = H1B19[datecol].dt.date
        
#     return H1B19


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
    
# read each csv to df and then concatenate
def combineCSV(input_dir, temp_dir, header_dir, outputfile, headerfile):    
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
    return df



if __name__ == "__main__":
    
    os.chdir(constants.CODE_DIR)
    code_dir = constants.CODE_DIR
    input_dir = constants.INPUT_DIR
    temp_dir = constants.TEMP_DIR
    header_dir = constants.HEADER_DIR
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # t3 = time.time()
    # H1B19_excel = pd.read_excel("../input/H-1B_Disclosure_Data_FY2019.xlsx", sheet_name=0)
    # t4 = time.time()
    # t_readexcel = t4 - t3
    # H1B19_excel_sub = H1B19_excel.iloc[:,:44].copy()

    # convert xlsx to csv for faster process
    t0 = time.time()
    xlsx2csv(input_dir)
    t1 = time.time()
    
    # read in csv to dataframe
    # csvCombine(in_dir, temp_dir)
    df = combineCSV(input_dir, temp_dir, header_dir, 
                    outputfile = 'h1b2015to2020.csv', headerfile = 'headers.csv')
    # df = pd.read_csv(temp_dir+'bigcsv.csv',parse_dates=['CASE_SUBMITTED'])

    df1 = df.sample(frac=0.001, replace=False, random_state=1).copy()
    df1.dtypes

    # H1B19 = cleanupH1B19(H1B19_csvfile = '../input/H-1B_Disclosure_Data_FY2019.csv')
    t2 = time.time()
    t_xlsx2csv = t1 - t0
    t_readcsv = t2 - t1
         

    # clean up data frame
    H1B19_v1 = H1B19.copy()
    H1B19_v1["EMPLOYER_NAME"]=H1B19_v1["EMPLOYER_NAME"].str.replace("INC.","INC")
    H1B19_v1['JOB_CATEGORY']=H1B19_v1['SOC_CODE'].apply(lambda x: jobClassifier(x))
    H1B19_v1['JOB_LEVEL']=H1B19_v1['JOB_TITLE'].apply(lambda x: levelClassifier(x))

    # get small set for navigation
    H1B19_sub = H1B19_v1.iloc[:1000,:].copy()   
    list(H1B19_sub.columns)    


    # count for important variable
    pd.options.plotting.backend = "plotly"
    
    H1B19_v1.groupby('JOB_LEVEL').count()[['CASE_NUMBER']].index
    
    # plot function
    fig = H1B19_v1.groupby('JOB_LEVEL').count()[['CASE_NUMBER']].plot()
    fig.show()





    # H1B19_excel_sub.iloc[600000, :5]
    # H1B19_csv_sub.iloc[700000,:5]
    
    H1B19_sub.head(5)



    