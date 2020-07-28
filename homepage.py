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
CODE_DIR = BASE_DIR + "h1permprediction/"
os.chdir(CODE_DIR)

import constants

temp_dir = constants.TEMP_DIR
model_dir = constants.MODEL_DIR

# load data and model
df = pd.read_csv(temp_dir + 'h1b2015to2020_sub.csv')

options_dict = {}
options_dict['MODEL'] = ['Pre-trained', 'User-defined']
options_dict['EMPLOYER_STATE'] = constants.STATE_DROPDOWN
options_dict['WORKSITE_STATE'] = constants.STATE_DROPDOWN
options_dict['JOB_CATEGORY'] = sorted(list(set(constants.JOB_CATEGORY_DROPDOWN)))
options_dict['JOB_LEVEL'] = constants.JOB_LEVEL_DROPDOWN
options_dict['FULL_TIME_POSITION'] = constants.FULL_TIME_POSITION_DROPDOWN
options_dict['PW_UNIT_OF_PAY'] = constants.PW_UNIT_OF_PAY_DROPDOWN
options_dict['PW_WAGE_LEVEL'] = sorted(list(set(constants.PW_WAGE_LEVEL_DROPDOWN)))
options_dict['H-1B_DEPENDENT'] = constants.H1B_DEPENDENT_DROPDOWN
options_dict['WILLFUL_VIOLATOR'] = constants.WILLFUL_VIOLATOR_DROPDOWN

options_dict['PERM_MODEL'] = ['Pre-trained', 'User-defined']
options_dict['PERM_WORKSITE_STATE'] = constants.STATE_DROPDOWN
options_dict['PERM_REFILE'] = constants.PERM_REFILE_DROPDOWN
options_dict['PERM_FW_OWNERSHIP_INTEREST'] = constants.PERM_FW_OWNERSHIP_INTEREST_DROPDOWN
options_dict['PERM_PW_LEVEL_9089'] = constants.PERM_PW_LEVEL_9089_DROPDOWN
options_dict['PERM_JOB_INFO_EDUCATION'] = constants.PERM_JOB_INFO_EDUCATION_DROPDOWN
options_dict['PERM_JOB_INFO_TRAINING'] = constants.PERM_JOB_INFO_TRAINING_DROPDOWN
options_dict['PERM_JOB_INFO_ALT_FIELD'] = constants.PERM_JOB_INFO_ALT_FIELD_DROPDOWN
options_dict['PERM_JOB_INFO_JOB_REQ_NORMAL'] = constants.PERM_JOB_INFO_JOB_REQ_NORMAL_DROPDOWN
options_dict['PERM_JOB_INFO_FOREIGN_LANG_REQ'] = constants.PERM_JOB_INFO_FOREIGN_LANG_REQ_DROPDOWN
options_dict['PERM_RECR_INFO_PROFESSIONAL_OCC'] = constants.PERM_RECR_INFO_PROFESSIONAL_OCC_DROPDOWN
options_dict['PERM_RECR_INFO_COLL_UNIV_TEACHER'] = constants.PERM_RECR_INFO_COLL_UNIV_TEACHER_DROPDOWN
options_dict['PERM_FW_INFO_BIRTH_COUNTRY'] = sorted(list(set(constants.PERM_FW_INFO_BIRTH_COUNTRY_DROPDOWN)))
options_dict['PERM_CLASS_OF_ADMISSION'] = sorted(list(set(constants.PERM_CLASS_OF_ADMISSION_DROPDOWN)))
options_dict['PERM_FW_INFO_TRAINING_COMP'] = constants.PERM_FW_INFO_TRAINING_COMP_DROPDOWN

options = {}
for key in options_dict:
    options[key] = [{'label': x, 'value': x} for x in options_dict[key]]

# df.set_index(df.iloc[:,0], drop = True, inplace = True)
# df = df.iloc[:,1:]

nav = Navbar()

body = dbc.Container(
    [
        html.Div([
            dbc.Row([html.H1("PREDICTION FOR H-1B & PERM")], justify="center", align="center", className="h-50"),
            dbc.Row([html.P('A dashboard for predicting success rate of H1B and PERM')], justify="center",
                    align="center", className="h-50"),
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
            dcc.Dropdown(id='EMPLOYER_STATE_dropdown', options=options['EMPLOYER_STATE'],
                         placeholder="Select employer state", value='CA')
        ]),
            dbc.Col([
                html.Div("Select worksite state"),
                dcc.Dropdown(id='WORKSITE_STATE_dropdown', options=options['WORKSITE_STATE'],
                             placeholder="Select worksite state", value='CA'),
            ]),
            dbc.Col([
                html.Div("Select a job category"),
                dcc.Dropdown(id='JOB_CATEGORY_dropdown', options=options['JOB_CATEGORY'],
                             placeholder="Select job category", value='COMPUTING, STATISTICIANS'),
            ]),
            dbc.Col([
                html.Div("Select your Job level"),
                dcc.Dropdown(id='JOB_LEVEL_dropdown', options=options['JOB_LEVEL'],
                             placeholder="Select job level", value='SENIOR')
            ]),
        ]
    ),
    html.Br(),
    dbc.Row(
        [dbc.Col([
            html.Div("Are you Full-time position worker?"),
            dcc.Dropdown(id='FULL_TIME_POSITION_dropdown', options=options['FULL_TIME_POSITION'],
                         placeholder="Select full-time position or not", value='Y')
        ]),
            dbc.Col([
                html.Div("What's your Wage unit of pay?"),
                dcc.Dropdown(id='PW_UNIT_OF_PAY_dropdown', options=options['PW_UNIT_OF_PAY'],
                             placeholder="Select wage unit of pay", value='HOUR')
            ]),
            dbc.Col([
                html.Div("Select your OES Wage level"),
                dcc.Dropdown(id='PW_WAGE_LEVEL_dropdown', options=options['PW_WAGE_LEVEL'],
                             placeholder="Select wage level", value='LEVEL II'),
            ]),
            dbc.Col([
                html.Div("Is there your employer H1B dependent?"),
                dcc.Dropdown(id='H-1B_DEPENDENT_dropdown', options=options['H-1B_DEPENDENT'],
                             placeholder="Select h1b dependent", value='N'),
            ]),
            dbc.Col([
                html.Div("Is your employer a Willful violator?"),
                dcc.Dropdown(id='WILLFUL_VIOLATOR_dropdown', options=options['WILLFUL_VIOLATOR'],
                             placeholder="Select willful violator of not", value='N'),
            ]),
        ]
    ),

    html.Br(),
    dbc.Row(
        [dbc.Col([
            html.Div("Model to use"),
            dcc.Dropdown(id='MODEL_dropdown', options=options['MODEL'],
                         placeholder="Select a model to use", value='Pre-trained'),
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
                html.Div("Select your worksite state"),
                dcc.Dropdown(id='PERM_WORKSITE_STATE_dropdown', options=options['PERM_WORKSITE_STATE'],
                             placeholder="Select worksite state", value='CA'),
            ]),
            dbc.Col([
                html.Div("Is it a refile?"),
                dcc.Dropdown(id='PERM_REFILE_dropdown', options=options['PERM_REFILE'],
                             placeholder="Select refile or not", value='N'),
            ]),
            dbc.Col([
                html.Div("Does foreign worker have ownership interest?"),
                dcc.Dropdown(id='PERM_FW_OWNERSHIP_INTEREST_dropdown', options=options['PERM_FW_OWNERSHIP_INTEREST'],
                             placeholder="Select ownership interest or not", value='N')
            ]),
            dbc.Col([
                html.Div("Select your OES skill level"),
                dcc.Dropdown(id='PERM_PW_LEVEL_9089_dropdown', options=options['PERM_PW_LEVEL_9089'],
                             placeholder="Select employer state", value='LEVEL II')
            ]),
            dbc.Col([
                html.Div("Select minimum education acceptable"),
                dcc.Dropdown(id='PERM_JOB_INFO_EDUCATION_dropdown', options=options['PERM_JOB_INFO_EDUCATION'],
                             placeholder="Select minimum education", value="MASTER'S")
            ]),
        ]
    ),
    html.Br(),
    dbc.Row(
        [dbc.Col([
            html.Div("Is training required?"),
            dcc.Dropdown(id='PERM_JOB_INFO_TRAINING_dropdown', options=options['PERM_JOB_INFO_TRAINING'],
                         placeholder="Select training required or not", value='Y')
        ]),
            dbc.Col([
                html.Div("Is the alternative field acceptable?"),
                dcc.Dropdown(id='PERM_JOB_INFO_ALT_FIELD_dropdown', options=options['PERM_JOB_INFO_ALT_FIELD'],
                             placeholder="Select accept alternative field or not", value='N')
            ]),
            dbc.Col([
                html.Div("Are job requirements normal?"),
                dcc.Dropdown(id='PERM_JOB_INFO_JOB_REQ_NORMAL_dropdown',
                             options=options['PERM_JOB_INFO_JOB_REQ_NORMAL'],
                             placeholder="Select job requirement normal or not", value='Y'),
            ]),
            dbc.Col([
                html.Div("Are foreign languages required?"),
                dcc.Dropdown(id='PERM_JOB_INFO_FOREIGN_LANG_REQ_dropdown',
                             options=options['PERM_JOB_INFO_FOREIGN_LANG_REQ'],
                             placeholder="Select foreign language required or not", value='N'),
            ]),
            dbc.Col([
                html.Div("Is it for a professional occupation?"),
                dcc.Dropdown(id='PERM_RECR_INFO_PROFESSIONAL_OCC_dropdown',
                             options=options['PERM_RECR_INFO_PROFESSIONAL_OCC'],
                             placeholder="Select professional occupation or not", value='Y'),
            ]),
        ]
    ),
    html.Br(),
    dbc.Row(
        [dbc.Col([
            html.Div("Applying for a college teacher?"),
            dcc.Dropdown(id='PERM_RECR_INFO_COLL_UNIV_TEACHER_dropdown',
                         options=options['PERM_RECR_INFO_COLL_UNIV_TEACHER'],
                         placeholder="Select college teacher or not", value='N')
        ]),
            dbc.Col([
                html.Div("What's your Birth country?"),
                dcc.Dropdown(id='PERM_FW_INFO_BIRTH_COUNTRY_dropdown', options=options['PERM_FW_INFO_BIRTH_COUNTRY'],
                             placeholder="Select worker birth country", value='INDIA')
            ]),
            dbc.Col([
                html.Div("Do you have any former admissions"),
                dcc.Dropdown(id='PERM_CLASS_OF_ADMISSION_dropdown', options=options['PERM_CLASS_OF_ADMISSION'],
                             placeholder="Select visa class", value='H-1B'),
            ]),
            dbc.Col([
                html.Div("Is the training done?"),
                dcc.Dropdown(id='PERM_FW_INFO_TRAINING_COMP_dropdown', options=options['PERM_FW_INFO_TRAINING_COMP'],
                             placeholder="Select foreign worker training complete or not",
                             value='A'),
            ]),
        ]
    ),

    html.Br(),
    dbc.Row(
        [dbc.Col([
            html.Div("Model to use"),
            dcc.Dropdown(id='PERM_MODEL_dropdown', options=options['PERM_MODEL'],
                         placeholder="Select a model to use", value='Pre-trained'),
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


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.UNITED])
app.layout = Homepage()

if __name__ == "__main__":
    app.run_server()
    
    # #!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# """
# Created on Sat Jun 27 15:03:17 2020

# @author: xuel12
# """

# ### Data
# import pandas as pd
# import numpy as np
# import pickle
# import time

# ### Graphing
# import plotly.graph_objects as go

# ### Dash
# import dash
# import dash_core_components as dcc
# import dash_html_components as html
# import dash_bootstrap_components as dbc
# from dash.dependencies import Output, Input, State
# import dash_daq as daq

# ## Navbar
# from navbar import Navbar

# import os
# BASE_DIR = "/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/"
# CODE_DIR = BASE_DIR+"h1permprediction/"
# os.chdir(CODE_DIR)

# import constants

# temp_dir = constants.TEMP_DIR
# model_dir = constants.MODEL_DIR

# # load data and model
# df = pd.read_csv(temp_dir+'h1b2015to2020_sub.csv')
    
# options_dict = {}
# options_dict['MODEL'] = ['Pre-trained', 'User-defined']
# options_dict['EMPLOYER_STATE'] = constants.STATE_DROPDOWN
# options_dict['WORKSITE_STATE'] = constants.STATE_DROPDOWN
# options_dict['JOB_CATEGORY'] = sorted(list(set(constants.JOB_CATEGORY_DROPDOWN)))
# options_dict['JOB_LEVEL'] = constants.JOB_LEVEL_DROPDOWN
# options_dict['FULL_TIME_POSITION'] = constants.FULL_TIME_POSITION_DROPDOWN
# options_dict['PW_UNIT_OF_PAY'] = constants.PW_UNIT_OF_PAY_DROPDOWN
# options_dict['PW_WAGE_LEVEL'] = sorted(list(set(constants.PW_WAGE_LEVEL_DROPDOWN)))
# options_dict['H-1B_DEPENDENT'] = constants.H1B_DEPENDENT_DROPDOWN
# options_dict['WILLFUL_VIOLATOR'] = constants.WILLFUL_VIOLATOR_DROPDOWN

# options_dict['PERM_MODEL'] = ['Pre-trained', 'User-defined']
# options_dict['PERM_WORKSITE_STATE'] = constants.STATE_DROPDOWN
# options_dict['PERM_REFILE'] = constants.PERM_REFILE_DROPDOWN
# options_dict['PERM_FW_OWNERSHIP_INTEREST'] = constants.PERM_FW_OWNERSHIP_INTEREST_DROPDOWN
# options_dict['PERM_PW_LEVEL_9089'] = constants.PERM_PW_LEVEL_9089_DROPDOWN
# options_dict['PERM_JOB_INFO_EDUCATION'] = constants.PERM_JOB_INFO_EDUCATION_DROPDOWN
# options_dict['PERM_JOB_INFO_TRAINING'] = constants.PERM_JOB_INFO_TRAINING_DROPDOWN
# options_dict['PERM_JOB_INFO_ALT_FIELD'] = constants.PERM_JOB_INFO_ALT_FIELD_DROPDOWN
# options_dict['PERM_JOB_INFO_JOB_REQ_NORMAL'] = constants.PERM_JOB_INFO_JOB_REQ_NORMAL_DROPDOWN
# options_dict['PERM_JOB_INFO_FOREIGN_LANG_REQ'] = constants.PERM_JOB_INFO_FOREIGN_LANG_REQ_DROPDOWN
# options_dict['PERM_RECR_INFO_PROFESSIONAL_OCC'] = constants.PERM_RECR_INFO_PROFESSIONAL_OCC_DROPDOWN
# options_dict['PERM_RECR_INFO_COLL_UNIV_TEACHER'] = constants.PERM_RECR_INFO_COLL_UNIV_TEACHER_DROPDOWN
# options_dict['PERM_FW_INFO_BIRTH_COUNTRY'] = sorted(list(set(constants.PERM_FW_INFO_BIRTH_COUNTRY_DROPDOWN)))
# options_dict['PERM_CLASS_OF_ADMISSION'] = sorted(list(set(constants.PERM_CLASS_OF_ADMISSION_DROPDOWN)))
# options_dict['PERM_FW_INFO_TRAINING_COMP'] = constants.PERM_FW_INFO_TRAINING_COMP_DROPDOWN


# options = {}
# for key in options_dict:
#     options[key] = [{'label':x, 'value': x} for x in options_dict[key]]


# # df.set_index(df.iloc[:,0], drop = True, inplace = True)
# # df = df.iloc[:,1:]

# nav = Navbar()

# body = dbc.Container(
#     [
#         html.Div([
#             dbc.Row([html.H1("PREDICTION FOR H-1B & PERM")], justify="center", align="center", className="h-50"),
#             dbc.Row([html.P('A dashboard for predicting success rate of H1B and PERM')], justify="center", align="center", className="h-50"),
#             html.Br(),
#         ]
#         ),
    
        
#     ],
#     className="mt-4",
# )

# h1b = dbc.Container([
#     html.H4("Predict new H1B application"),

#     dbc.Row(
#             [dbc.Col([
#                 html.Div("Select employer state"),
#                 dcc.Dropdown(id = 'EMPLOYER_STATE_dropdown', options = options['EMPLOYER_STATE'], 
#                              placeholder="Select employer state", value = 'CA')
#                 ]),
#             dbc.Col([
#                 html.Div("Select worksite state"),
#                 dcc.Dropdown(id = 'WORKSITE_STATE_dropdown', options = options['WORKSITE_STATE'], 
#                              placeholder="Select worksite state", value = 'CA'),
#                 ]),
#             dbc.Col([
#                 html.Div("Select job category"),
#                 dcc.Dropdown(id = 'JOB_CATEGORY_dropdown', options = options['JOB_CATEGORY'], 
#                              placeholder="Select job category", value = 'COMPUTING, STATISTICIANS'),
#                 ]),
#             dbc.Col([
#                 html.Div("Job level"),
#                 dcc.Dropdown(id = 'JOB_LEVEL_dropdown', options = options['JOB_LEVEL'], 
#                              placeholder="Select job level", value = 'SENIOR')
#                 ]),
#             ]
#         ),
#     html.Br(),
#     dbc.Row(
#             [dbc.Col([
#                 html.Div("Full-time position?"),
#                 dcc.Dropdown(id = 'FULL_TIME_POSITION_dropdown', options = options['FULL_TIME_POSITION'], 
#                              placeholder="Select full-time position or not", value = 'Y')
#                 ]),
#             dbc.Col([
#                 html.Div("Wage unit of pay?"),
#                 dcc.Dropdown(id = 'PW_UNIT_OF_PAY_dropdown', options = options['PW_UNIT_OF_PAY'], 
#                              placeholder="Select wage unit of pay", value = 'HOUR')
#                 ]),
#             dbc.Col([
#                 html.Div("Wage level"),
#                 dcc.Dropdown(id = 'PW_WAGE_LEVEL_dropdown', options = options['PW_WAGE_LEVEL'], 
#                              placeholder="Select wage level", value = 'LEVEL II'),
#                 ]),
#             dbc.Col([
#                 html.Div("Is there a dependent?"),
#                 dcc.Dropdown(id = 'H-1B_DEPENDENT_dropdown', options = options['H-1B_DEPENDENT'], 
#                              placeholder="Select h1b dependent", value = 'N'),
#                 ]),
#             dbc.Col([
#                 html.Div("Willful violator?"),
#                 dcc.Dropdown(id = 'WILLFUL_VIOLATOR_dropdown', options = options['WILLFUL_VIOLATOR'], 
#                              placeholder="Select willful violator of not", value = 'N'),
#                 ]),
#             ]
#         ),
    
#     html.Br(),
#     dbc.Row(
#             [dbc.Col([
#                 html.Div("Model to use"),
#                 dcc.Dropdown(id = 'MODEL_dropdown', options = options['MODEL'], 
#                              placeholder="Select a model to use", value = 'Pre-trained'),
#                 ]),
#             dbc.Col([
#                 # html.Div("Model to use"),
#                 daq.Indicator(id='predict-indicator', label="Red:Default Model, Blue:User Model",
#                               value=True, color='red'),
#                 ]),
#             ]),
#     # prediction
#     html.Br(),
#     # html.Div(
#     #     [
#     #         dbc.Button("Start/Reset prediction", id="submit-predict", n_clicks=0),
#     #         dbc.Spinner(html.Div(id="submitting-predict")),
#     #     ]
#     # ),
#     dbc.Row([
#         dbc.Col([
#             dbc.Button("Start/Reset prediction", id="submit-predict", n_clicks=0),
#             ]),
#         dbc.Col([
#             dbc.Spinner(html.Div(id="submitting-predict")),
#             ]),
#         ]
#         ),
        
#     # prediction graph
#     html.Br(),
#     html.Div(id='my-output'),
#     html.Br(),
#     html.Br(),
#     html.Br(),

#     # dbc.Row(
#     #         [
#     #             html.Div(
#     #                 [dcc.Graph(id="h1b_graph")],
#     #                 className="pretty_container",
#     #             ),
#     #         ],
#     #         ),
#     ]
#     # style=dict(display='flex')
# )

    
    
# perm = dbc.Container([
#     html.H4("Predict new PERM application"),

#     dbc.Row(
#             [
#             dbc.Col([
#                 html.Div("Select worksite state"),
#                 dcc.Dropdown(id = 'PERM_WORKSITE_STATE_dropdown', options = options['PERM_WORKSITE_STATE'], 
#                              placeholder="Select worksite state", value = 'CA'),
#                 ]),
#             dbc.Col([
#                 html.Div("Is it a refile?"),
#                 dcc.Dropdown(id = 'PERM_REFILE_dropdown', options = options['PERM_REFILE'], 
#                              placeholder="Select refile or not", value = 'N'),
#                 ]),
#             dbc.Col([
#                 html.Div("Does foreign worker has ownership interest?"),
#                 dcc.Dropdown(id = 'PERM_FW_OWNERSHIP_INTEREST_dropdown', options = options['PERM_FW_OWNERSHIP_INTEREST'], 
#                              placeholder="Select ownership interest or not", value = 'N')
#                 ]),
#             dbc.Col([
#                 html.Div("Select skill level"),
#                 dcc.Dropdown(id = 'PERM_PW_LEVEL_9089_dropdown', options = options['PERM_PW_LEVEL_9089'], 
#                              placeholder="Select employer state", value = 'LEVEL II')
#                 ]),
#             dbc.Col([
#                 html.Div("Select minimum education acceptable"),
#                 dcc.Dropdown(id = 'PERM_JOB_INFO_EDUCATION_dropdown', options = options['PERM_JOB_INFO_EDUCATION'], 
#                              placeholder="Select minimum education", value = "MASTER'S")
#                 ]),
#             ]
#         ),
#     html.Br(),
#     dbc.Row(
#             [dbc.Col([
#                 html.Div("Is training required?"),
#                 dcc.Dropdown(id = 'PERM_JOB_INFO_TRAINING_dropdown', options = options['PERM_JOB_INFO_TRAINING'], 
#                              placeholder="Select training required or not", value = 'Y')
#                 ]),
#             dbc.Col([
#                 html.Div("Is the alternative field acceptable?"),
#                 dcc.Dropdown(id = 'PERM_JOB_INFO_ALT_FIELD_dropdown', options = options['PERM_JOB_INFO_ALT_FIELD'], 
#                              placeholder="Select accept alternative field or not", value = 'N')
#                 ]),
#             dbc.Col([
#                 html.Div("Is job requirements are normal"),
#                 dcc.Dropdown(id = 'PERM_JOB_INFO_JOB_REQ_NORMAL_dropdown', options = options['PERM_JOB_INFO_JOB_REQ_NORMAL'], 
#                              placeholder="Select job requirement normal or not", value = 'Y'),
#                 ]),
#             dbc.Col([
#                 html.Div("Is foreign language required?"),
#                 dcc.Dropdown(id = 'PERM_JOB_INFO_FOREIGN_LANG_REQ_dropdown', options = options['PERM_JOB_INFO_FOREIGN_LANG_REQ'], 
#                              placeholder="Select foreign language required or not", value = 'N'),
#                 ]),
#             dbc.Col([
#                 html.Div("Is it for a professional occupation?"),
#                 dcc.Dropdown(id = 'PERM_RECR_INFO_PROFESSIONAL_OCC_dropdown', options = options['PERM_RECR_INFO_PROFESSIONAL_OCC'], 
#                              placeholder="Select professional occupation or not", value = 'Y'),
#                 ]),
#             ]
#         ),
#     html.Br(),
#     dbc.Row(
#             [dbc.Col([
#                 html.Div("Apply for a college teacher?"),
#                 dcc.Dropdown(id = 'PERM_RECR_INFO_COLL_UNIV_TEACHER_dropdown', options = options['PERM_RECR_INFO_COLL_UNIV_TEACHER'], 
#                              placeholder="Select college teacher or not", value = 'N')
#                 ]),
#             dbc.Col([
#                 html.Div("Birth country?"),
#                 dcc.Dropdown(id = 'PERM_FW_INFO_BIRTH_COUNTRY_dropdown', options = options['PERM_FW_INFO_BIRTH_COUNTRY'], 
#                              placeholder="Select worker birth country", value = 'INDIA')
#                 ]),
#             dbc.Col([
#                 html.Div("Visa class"),
#                 dcc.Dropdown(id = 'PERM_CLASS_OF_ADMISSION_dropdown', options = options['PERM_CLASS_OF_ADMISSION'], 
#                              placeholder="Select visa class", value = 'H-1B'),
#                 ]),
#             dbc.Col([
#                 html.Div("Is the training done?"),
#                 dcc.Dropdown(id = 'PERM_FW_INFO_TRAINING_COMP_dropdown', options = options['PERM_FW_INFO_TRAINING_COMP'], 
#                              placeholder="Select foreign worker training complete or not",
#                              value = 'A'),
#                 ]),
#             ]
#         ),
    
#     html.Br(),
#     dbc.Row(
#             [dbc.Col([
#                 html.Div("Model to use"),
#                 dcc.Dropdown(id = 'PERM_MODEL_dropdown', options = options['PERM_MODEL'], 
#                              placeholder="Select a model to use", value = 'Pre-trained'),
#                 ]),
#             dbc.Col([
#                 # html.Div("Model to use"),
#                 daq.Indicator(id='predict-indicator-perm', label="Red:Default Model, Blue:User Model",
#                               value=True, color='red'),
#                 ]),
#             ]),
#     # prediction
#     html.Br(),
#     # html.Div(
#     #     [
#     #         dbc.Button("Start/Reset prediction", id="submit-predict", n_clicks=0),
#     #         dbc.Spinner(html.Div(id="submitting-predict")),
#     #     ]
#     # ),
#     dbc.Row([
#         dbc.Col([
#             dbc.Button("Start/Reset prediction", id="submit-predict-perm", n_clicks=0),
#             ]),
#         dbc.Col([
#             dbc.Spinner(html.Div(id="submitting-predict-perm")),
#             ]),
#         ]
#         ),
        
#     # prediction graph
#     html.Br(),
#     html.Div(id='my-output-perm'),

#     # dbc.Row(
#     #         [
#     #             html.Div(
#     #                 [dcc.Graph(id="h1b_graph")],
#     #                 className="pretty_container",
#     #             ),
#     #         ],
#     #         ),
#     ]
#     # style=dict(display='flex')
# )

# def Homepage():
#     layout = html.Div([
#         nav,
# 	    body,
#         h1b,
#         perm
#     ])
#     return layout

# app = dash.Dash(__name__, external_stylesheets = [dbc.themes.UNITED])
# app.layout = Homepage()


    

    
# if __name__ == "__main__":
#     app.run_server()