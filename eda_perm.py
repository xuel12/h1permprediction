import os

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

import plotly
# import getpass
import plotly.graph_objs as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

from navbar import Navbar

import pickle

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
    
nav = Navbar()

pickle_in_perm = open(temp_dir + "edaPERM.pickle","rb")

# if not os.path.exists(input_dir):
#     os.makedirs(input_dir)
edaplotPERM = pickle.load(pickle_in_perm)


# fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])
# fig = px.pie(edaplot['EMPLOYER_STATE'], values='CASE_STATUS', names='CASE_STATUS', title='Population of European continent')




############################################################################################################
fig_case_status_perm = go.Figure(data=[go.Bar(x=edaplotPERM['CASE_STATUS'].index,
                                       y=edaplotPERM['CASE_STATUS']['countvar'])])

fig_employer_state_perm = go.Figure(data=[go.Pie(labels=edaplotPERM['EMPLOYER_STATE'].index,
                                             values=edaplotPERM['EMPLOYER_STATE']['countvar'])])

fig_worksite_state_perm = go.Figure(data=[go.Pie(labels=edaplotPERM['WORKSITE_STATE'].index,
                                             values=edaplotPERM['WORKSITE_STATE']['countvar'])])

t1_wage_perm = go.Bar(x=edaplotPERM['PW_WAGE_LEVEL'][edaplotPERM['PW_WAGE_LEVEL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['PW_LEVEL_9089'].values,y=edaplotPERM['PW_WAGE_LEVEL'][edaplotPERM['PW_WAGE_LEVEL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_wage_perm = go.Bar(x=edaplotPERM['PW_WAGE_LEVEL'][edaplotPERM['PW_WAGE_LEVEL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['PW_LEVEL_9089'].values,y=edaplotPERM['PW_WAGE_LEVEL'][edaplotPERM['PW_WAGE_LEVEL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_wage_level_perm = go.Figure(data=[t1_wage_perm,t2_wage_perm])
fig_wage_level_perm.update_layout(barmode='stack')

t1_refile_perm = go.Bar(x=edaplotPERM['REFILE'][edaplotPERM['REFILE'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['REFILE'].values,y=edaplotPERM['REFILE'][edaplotPERM['REFILE'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_refile_perm = go.Bar(x=edaplotPERM['REFILE'][edaplotPERM['REFILE'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['REFILE'].values,y=edaplotPERM['REFILE'][edaplotPERM['REFILE'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_refile_perm = go.Figure(data=[t1_refile_perm,t2_refile_perm])
fig_refile_perm.update_layout(barmode='stack')

t1_edu_perm = go.Bar(x=edaplotPERM['EDUCATION'][edaplotPERM['EDUCATION'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['FOREIGN_WORKER_INFO_EDUCATION'].values,y=edaplotPERM['EDUCATION'][edaplotPERM['EDUCATION'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_edu_perm = go.Bar(x=edaplotPERM['EDUCATION'][edaplotPERM['EDUCATION'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['FOREIGN_WORKER_INFO_EDUCATION'].values,y=edaplotPERM['EDUCATION'][edaplotPERM['EDUCATION'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_edu_perm = go.Figure(data=[t1_edu_perm,t2_edu_perm])
fig_edu_perm.update_layout(barmode='stack')

t1_alt_perm = go.Bar(x=edaplotPERM['JOB_INFO_ALT_FIELD'][edaplotPERM['JOB_INFO_ALT_FIELD'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['JOB_INFO_ALT_FIELD'].values,y=edaplotPERM['JOB_INFO_ALT_FIELD'][edaplotPERM['JOB_INFO_ALT_FIELD'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_alt_perm = go.Bar(x=edaplotPERM['JOB_INFO_ALT_FIELD'][edaplotPERM['JOB_INFO_ALT_FIELD'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['JOB_INFO_ALT_FIELD'].values,y=edaplotPERM['JOB_INFO_ALT_FIELD'][edaplotPERM['JOB_INFO_ALT_FIELD'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_alt_perm = go.Figure(data=[t1_alt_perm,t2_alt_perm])
fig_alt_perm.update_layout(barmode='stack')

t1_coun_perm = go.Bar(x=edaplotPERM['FW_INFO_BIRTH_COUNTRY'][edaplotPERM['FW_INFO_BIRTH_COUNTRY'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['FW_INFO_BIRTH_COUNTRY'].values,y=edaplotPERM['FW_INFO_BIRTH_COUNTRY'][edaplotPERM['FW_INFO_BIRTH_COUNTRY'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_coun_perm = go.Bar(x=edaplotPERM['FW_INFO_BIRTH_COUNTRY'][edaplotPERM['FW_INFO_BIRTH_COUNTRY'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['FW_INFO_BIRTH_COUNTRY'].values,y=edaplotPERM['FW_INFO_BIRTH_COUNTRY'][edaplotPERM['FW_INFO_BIRTH_COUNTRY'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_coun_perm = go.Figure(data=[t1_coun_perm,t2_coun_perm])
fig_coun_perm.update_layout(barmode='stack')

t1_adm_perm = go.Bar(x=edaplotPERM['CLASS_OF_ADMISSION'][edaplotPERM['CLASS_OF_ADMISSION'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['CLASS_OF_ADMISSION'].values,y=edaplotPERM['CLASS_OF_ADMISSION'][edaplotPERM['CLASS_OF_ADMISSION'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_adm_perm = go.Bar(x=edaplotPERM['CLASS_OF_ADMISSION'][edaplotPERM['CLASS_OF_ADMISSION'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['CLASS_OF_ADMISSION'].values,y=edaplotPERM['CLASS_OF_ADMISSION'][edaplotPERM['CLASS_OF_ADMISSION'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_adm_perm = go.Figure(data=[t1_adm_perm,t2_adm_perm])
fig_adm_perm.update_layout(barmode='stack')

t1_train_perm = go.Bar(x=edaplotPERM['FW_INFO_TRAINING_COMP'][edaplotPERM['FW_INFO_TRAINING_COMP'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['FW_INFO_TRAINING_COMP'].values,y=edaplotPERM['FW_INFO_TRAINING_COMP'][edaplotPERM['FW_INFO_TRAINING_COMP'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_train_perm = go.Bar(x=edaplotPERM['FW_INFO_TRAINING_COMP'][edaplotPERM['FW_INFO_TRAINING_COMP'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['FW_INFO_TRAINING_COMP'].values,y=edaplotPERM['FW_INFO_TRAINING_COMP'][edaplotPERM['FW_INFO_TRAINING_COMP'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_train_perm = go.Figure(data=[t1_train_perm,t2_train_perm])
fig_train_perm.update_layout(barmode='stack')

t1_require_perm = go.Bar(x=edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'][edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['JOB_INFO_JOB_REQ_NORMAL'].values,y=edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'][edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_require_perm = go.Bar(x=edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'][edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['JOB_INFO_JOB_REQ_NORMAL'].values,y=edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'][edaplotPERM['JOB_INFO_JOB_REQ_NORMAL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_require_perm = go.Figure(data=[t1_require_perm,t2_require_perm])
fig_require_perm.update_layout(barmode='stack')

body = dbc.Container(
    [
        html.P(
            """ This page is to showing the PERM summary from year 2015 to 2019."""
        ),
        # dbc.Button("View details", color="secondary"),

        html.H3("CASE_STATUS OVER 5 YEARS"),
        dbc.Row(
            [
                dcc.Graph(
                    id='case_status_perm',
                    figure=fig_case_status_perm ,
                ),
            ]
        ),

        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("EMPLOYER_STATE"),
                        dcc.Graph(
                            id='employer_state_perm',
                            figure=fig_employer_state_perm,
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("WORKSITE_STATE"),
                        dcc.Graph(
                            id='worksite_state_perm',
                            figure=fig_worksite_state_perm,
                        ),
                    ]
                ),
            ]
        ),

        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("REFILE STATUS"),
                        dcc.Graph(
                            id='refile_perm',
                            figure=fig_refile_perm,
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("EDUCATION LEVEL"),
                        dcc.Graph(
                            id='edu_perm',
                            figure=fig_edu_perm,
                        ),
                    ]
                ),

            ]
        ),

        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("JOB ALTERNATE FIELD"),
                        dcc.Graph(
                            id='job_alt_perm',
                            figure=fig_alt_perm,
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("PW_WAGE_LEVEL"),
                        dcc.Graph(
                            id='wage_level_perm',
                            figure=fig_wage_level_perm,
                        ),
                    ]
                ),

            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H4("TOP APPLY COUNTRIES"),
                        dcc.Graph(
                            id='job_coun_perm',
                            figure=fig_coun_perm ,
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H4("FORMER ADMISSIONS"),
                        dcc.Graph(
                            id='job_adm_perm',
                            figure=fig_adm_perm,
                        ),
                    ]
                ),
            ]
        ),

        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3("TRAINING STATUS"),
                        dcc.Graph(
                            id='job_train_perm',
                            figure=fig_train_perm,
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        html.H3("JOB REQUIREMENTS"),
                        dcc.Graph(
                            id='job_require_perm',
                            figure=fig_require_perm,
                        ),
                    ]
                ),
            ]
        )

    ],

    className="mt-4",
)



def EDA_perm():
    layout = html.Div([
        nav,
        body
    ])
    return layout





app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = EDA_perm()

if __name__ == "__main__":
    app.run_server()