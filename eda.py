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

pickle_in = open(temp_dir + "eda.pickle","rb")

# if not os.path.exists(input_dir):
#     os.makedirs(input_dir)
edaplot = pickle.load(pickle_in)


# fig = px.scatter(df, x="x", y="y", color="fruit", custom_data=["customdata"])
# fig = px.pie(edaplot['EMPLOYER_STATE'], values='CASE_STATUS', names='CASE_STATUS', title='Population of European continent')

fig_employter_state = go.Figure(data=[go.Pie(labels=edaplot['EMPLOYER_STATE'].index, 
                                             values=edaplot['EMPLOYER_STATE']['CASE_STATUS'])],
                                # layout = {'title':'EMPLOYER_STATE'}
                                )
fig_worksite_state = go.Figure(data=[go.Pie(labels=edaplot['WORKSITE_STATE'].index, 
                             values=edaplot['WORKSITE_STATE']['CASE_STATUS'])])

fig_job_category = go.Figure(data=[go.Bar(x=edaplot['JOB_CATEGORY'].index,
                                             y=edaplot['JOB_CATEGORY']['CASE_STATUS'])])

t1_job = go.Bar(x=edaplot['JOB_LEVEL'][edaplot['JOB_LEVEL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['JOB_LEVEL'].values,y=edaplot['JOB_LEVEL'][edaplot['JOB_LEVEL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_job = go.Bar(x=edaplot['JOB_LEVEL'][edaplot['JOB_LEVEL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['JOB_LEVEL'].values,y=edaplot['JOB_LEVEL'][edaplot['JOB_LEVEL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_job_level = go.Figure(data=[t1_job,t2_job])
fig_job_level.update_layout(barmode='stack')

fig_fulltime = go.Figure(data=[go.Bar(x=edaplot['FULL_TIME_POSITION'].index,
                                             y=edaplot['FULL_TIME_POSITION']['CASE_STATUS'])])

t1_wage = go.Bar(x=edaplot['PW_WAGE_LEVEL'][edaplot['PW_WAGE_LEVEL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['PW_WAGE_LEVEL'].values,y=edaplot['PW_WAGE_LEVEL'][edaplot['PW_WAGE_LEVEL'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_wage = go.Bar(x=edaplot['PW_WAGE_LEVEL'][edaplot['PW_WAGE_LEVEL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['PW_WAGE_LEVEL'].values,y=edaplot['PW_WAGE_LEVEL'][edaplot['PW_WAGE_LEVEL'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_wage_level = go.Figure(data=[t1_wage,t2_wage])
fig_wage_level.update_layout(barmode='stack')

t1_dep = go.Bar(x=edaplot['H-1B_DEPENDENT'][edaplot['H-1B_DEPENDENT'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['H-1B_DEPENDENT'].values,y=edaplot['H-1B_DEPENDENT'][edaplot['H-1B_DEPENDENT'].CASE_STATUS == 'CERTIFIED'].sort_values('countvar',ascending= False)['countvar'].values,name='CERTIFIED')
t2_dep = go.Bar(x=edaplot['H-1B_DEPENDENT'][edaplot['H-1B_DEPENDENT'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['H-1B_DEPENDENT'].values,y=edaplot['H-1B_DEPENDENT'][edaplot['H-1B_DEPENDENT'].CASE_STATUS == 'DENIED'].sort_values('countvar',ascending= False)['countvar'].values,name='DENIED')
fig_h1b_dependent = go.Figure(data=[t1_dep,t2_dep])
fig_h1b_dependent.update_layout(barmode='stack')


fig_willful_violator = go.Figure(data=[go.Bar(x=edaplot['WILLFUL_VIOLATOR'].index,
                                       y=edaplot['WILLFUL_VIOLATOR']['CASE_STATUS'])])

fig_submit_date = go.Figure(data=[go.Scatter(
    x=edaplot['CASE_SUBMITTED'].index,
    y=edaplot['CASE_SUBMITTED']['DENIED']/(edaplot['CASE_SUBMITTED']['CERTIFIED']+edaplot['CASE_SUBMITTED']['DENIED']),
    mode='lines+markers')]
    )
fig_submit_date.update_xaxes(tickangle=-90, tickfont=dict(size=12))
fig_submit_date.update_layout(xaxis_title='Month',yaxis_title='DENIED Rate')


body = dbc.Container(
    [
        html.P(
            """ This page is to showing the H1B summary from year 2015 to 2019."""
              ),
        # dbc.Button("View details", color="secondary"),
        
        html.H3("Denied Rate OVER 5 YEARS"),
        dbc.Row(
        [
            dcc.Graph(
                        id='submit_date',
                        figure = fig_submit_date,
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
                            id='employer_state',
                            figure = fig_employter_state,
                        ),
                    ]
                ),
            dbc.Col(
                    [
                        html.H4("WORKSITE_STATE"),
                        dcc.Graph(
                            id='worksite_state',
                            figure = fig_worksite_state,
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
                        html.H4("JOB_CATEGORY"),
                        dcc.Graph(
                            id='job_category',
                            figure = fig_job_category,
                        ),
                    ]
                ),
            dbc.Col(
                    [
                        html.H4("JOB_LEVEL"),
                        dcc.Graph(
                            id='job_level',
                            figure = fig_job_level,
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
                        html.H4("FULL_TIME_POSITION"),
                        dcc.Graph(
                            id='fulltime_position',
                            figure = fig_fulltime,
                        ),
                    ]
                ),
            dbc.Col(
                    [
                        html.H4("PW_WAGE_LEVEL"),
                        dcc.Graph(
                            id='wage_level',
                            figure = fig_wage_level,
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
                        html.H3("H-1B_DEPENDENT"),
                        dcc.Graph(
                            id='h1b_dependent',
                            figure = fig_h1b_dependent,
                        ),
                    ]
                ),
            dbc.Col(
                    [
                        html.H3("WILLFUL_VIOLATOR"),
                        dcc.Graph(
                            id='willful_violator',
                            figure = fig_willful_violator,
                        ),
                    ]
                ),
        ]
        ),
    ],
    className="mt-4",
)


def EDA():
    layout = html.Div([
        nav,
	    body,
    ])
    return layout





app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
app.layout = EDA()

if __name__ == "__main__":
    app.run_server()