import base64
import datetime
import io

# import wrangling
# import prediction
# import training
# import constants
import os
from urllib.parse import quote as urlquote
# from sklearn.metrics import roc_auc_score, roc_curve, auc
import pandas as pd

import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
import dash_core_components as dcc
import dash_table

import dash_daq as daq
from flask import Flask, send_from_directory
from random import random
import plotly.express as px

# # os.chdir('F:/5500_P1_MVP/data')
# BASE_DIR = '/Users/xuel12/Documents/MSdatascience/DS5500datavis/project2/'
# CODE_DIR = BASE_DIR + 'h1permprediction/'
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
    
default_train_df = pd.read_csv(temp_dir + 'bigcsv.csv')
# default_feature_importance = pd.read_csv(CODE_DIR + 'default_feature_importance.csv')
# default_figure_feature_importance = {
#             'data': [
#                 {'x': default_feature_importance['m/z scope'].tolist(), 'y': default_feature_importance['importance'].tolist(), 'type': 'bar'}
#             ],
#             'layout': {
#                 'title': 'feature importance will be displayed below'
#             }
#         }
# default_roc_curve = px.line(default_train_df, x="fpr", y="tpr", title='ROC curve will be displayed below')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


@server.route(constants.DOWNLOAD_DIR + "<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(input_dir, path, as_attachment=True)

app.layout = html.Div([
    html.H1("PREDICTION FOR H-1B & PERM"),
    html.H4("Please specify the base directory"),
    # html.Div(dcc.Input(id='input-on-submit', type='text', value='F:/5500_P1_MVP/')), #add an input bar
    html.Div(dcc.Input(id='input-on-submit', type='text',
                       value=base_path)),  # add an input bar
    html.H4("Upload a new dataset:"),
    # upload new data
    dcc.Upload(
        id="upload-data",
        children=html.Div(
            ["Drag and drop or click to select a file to upload."]
        ),
        style={
            "width": "100%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px",
        },
        max_size=-1,
        multiple=True,
    ),

    html.H2("Training"),
    html.H6("---------------------------------------------------------------------------------------------"), 
    html.H4('Hyper-parameter tuning scope selection'),
    html.H6("[NUMBER OF ESTIMATORS]"),
    html.Div(id='output-container-range-slider'),
    dcc.RangeSlider(
        id='n_estimators_RangeSlider',
        min=50,
        max=250,
        step=50,
        value=[50, 100],marks = {50:'50',100:'100',150:'150',200:'200',250:'250'}
    ),
    html.H6("[MINIMAL NUMBER OF SAMPLES IN A LEAF]"),
    html.Div(id='output-min_samples_leaf_RangeSlider'),
    dcc.RangeSlider(
        id='min_samples_leaf_RangeSlider',
        min=2,
        max=32,
        step=2,
        value=[2, 8],marks = {2:'2',4:'4',8:'8',16:'16',32:'32'}
    ),
    html.Button('Start/stop training', id='submit-val', n_clicks=0),  # add a button to start training
    daq.Indicator(id='train-indicator',label="Training in process",value=True,color='grey'),
    html.Div(id='spectrum quality training',children='AUC score:___'),  # add a section to store and display output

    html.H2("Prediction"),
    html.Button('Start/stop prediction', id='submit-pred', n_clicks=0),  # add a button to start training
    daq.Indicator(id='predict-indicator',label="Prediction in process",value=True,color='grey'),
    html.Div(id='spectrum quality prediction',children='prediction result-positive rate:___'),  # add a section to store and display output
    
    html.H3("File List"),
    html.Ul(id="file-list"),
    # Hidden div inside the app that stores the intermediate value
    html.Div(id='intermediate-value-1', style={'display': 'none'}),
    html.Div(id='intermediate-value-2', style={'display': 'none'}),
    # html.H3("Feature importance"),
    # dcc.Graph(id='important-features-graph',figure=default_figure_feature_importance),
    # html.H3("ROC curve"),
    # dcc.Graph(id='ROC curve',figure = default_roc_curve)

])

    

@app.callback(
    [dash.dependencies.Output('important-features-graph', 'figure'),
     dash.dependencies.Output('spectrum quality training', 'children'),
     dash.dependencies.Output('ROC curve','figure')],
    # specify the component and its property that shall contain the output
    [dash.dependencies.Input('submit-val', 'n_clicks')],
    # specify the component and corresponding properties that shall serve as input
    [dash.dependencies.State('input-on-submit',
                             'value')])  # specify the component and corresponding properties that shall serve as input
def update_output_train(n_clicks, value):  # define the function reaching output from input
    if n_clicks % 2 is 1:
        BASE_PATH = value  # input value gives the base directory
        CODE_DIR = BASE_PATH + "spectrumQC/"
        DATA_DIR = BASE_PATH + "data/"

        TEMP_DIR = BASE_PATH + "temp/"
        MODEL_DIR = BASE_PATH + "model/"
        OUT_DIR = BASE_PATH + "output/"
        BIN_SIZE = 10

        os.chdir(CODE_DIR)
        data_dir = DATA_DIR
        temp_dir = TEMP_DIR
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        model_dir = MODEL_DIR
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        out_dir = OUT_DIR
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        bin_size = BIN_SIZE

        # prepare training set
        # mzML_file_names = wrangling.mzMLfilename(data_dir)
        # parse mzML files to dictionary
        # wrangling.mzML2dict(data_dir, temp_dir, bin_size)
        # wrangling.evidenceDF(data_dir, temp_dir)
        # training.trainingDataset(temp_dir, bin_size, mzML_file_names)

        param_grid = {'rf': {"min_samples_leaf": [2], "min_samples_split": [5], "n_estimators": [50]}, \
                      'svm': {"kernel": ['linear']},
                      'mlp': {"activation" : ['relu']}}
        
        final_result = training.modelling_spectrum_quality(temp_dir, model_dir, method='rf', param_grid=param_grid)
        X_train = final_result['X_train']
        y_train = final_result['y_train']
        X_test = final_result['X_test']
        y_test = final_result['y_test']
        final_model = final_result['model']
        feature_scores = pd.Series(final_model.feature_importances_, index=X_train.columns).sort_values(ascending=False)
        fpr, tpr, thresholds = roc_curve(y_test, final_model.predict_proba(X_test)[:, 1])
        # feature_scores_df = pd.Series(final_model.feature_importances_, index=X_train.columns).sort_values(
        #     ascending=False).reset_index()
        # fig = px.scatter(feature_scores_df, x="interval", y=0)
        figure_feature_importance = {'data':[dict(x=feature_scores.index.tolist(),y=feature_scores.tolist())],'layout': {'title': 'important features distribution'}}
        figure_roc_curve = {'data':[dict(x=fpr.tolist(),y=tpr.tolist())],'layout': {'title': 'roc curve'}}
        return figure_feature_importance,'AUC score of training process is "{}"'.format(roc_auc_score(y_test, final_model.predict_proba(X_test)[:, 1])), figure_roc_curve
    else:
        return default_figure_feature_importance, '', default_roc_curve


# @app.callback(
#     dash.dependencies.Output('train-indicator', 'color'),
#     # specify the component and its property that shall contain the output
#     [dash.dependencies.Input('submit-val', 'n_clicks')])
# def start_train_indicator_button(n_clicks):
#     if n_clicks % 2 is 1:
#         value = 'red'
#     else:
#         value = 'grey'
#     return value

# @app.callback(
#     dash.dependencies.Output('predict-indicator', 'color'),
#     # specify the component and its property that shall contain the output
#     [dash.dependencies.Input('submit-pred', 'n_clicks')])
# def start_train_indicator_button(n_clicks):
#     if n_clicks % 2 is 1:
#         value = 'red'
#     else:
#         value = 'grey'
#     return value



# @app.callback(
#     dash.dependencies.Output('spectrum quality prediction', 'children'),
#     # specify the component and its property that shall contain the output
#     [dash.dependencies.Input('submit-pred', 'n_clicks')],
#     # specify the component and corresponding properties that shall serve as input
#     [dash.dependencies.State('input-on-submit',
#                              'value')]) # specify the component and corresponding properties that shall serve as input
# def update_output_pred(n_clicks, value):  # define the function reaching output from input
#     if n_clicks % 2 is 1:
#         BASE_PATH = value  # input value gives the base directory

#         CODE_DIR = BASE_PATH + "spectrumQC/"
#         PREDICT_DIR = BASE_PATH + "predict/"

#         MODEL_DIR = BASE_PATH + "model/"
#         OUT_DIR = BASE_PATH + "output/"
#         BIN_SIZE = 10

#         os.chdir(CODE_DIR)
#         predict_dir = PREDICT_DIR

#         model_dir = MODEL_DIR
#         if not os.path.exists(model_dir):
#             os.makedirs(model_dir)
#         out_dir = OUT_DIR
#         if not os.path.exists(out_dir):
#             os.makedirs(out_dir)
#         bin_size = BIN_SIZE

#         # prepare prediction set
#         # predictfile_names = wrangling.mzMLfilename(predict_dir)
#         # wrangling.mzML2dict(predict_dir, predict_dir, bin_size)
#         # prediction.predictDataset(predict_dir, bin_size, predictfile_names)

#         # apply trained model for prediction
#         prediction_result = prediction.predict_spectrum_quality(predict_dir, model_dir, out_dir)
#         return 'prediction complete, please find the result in directory'
#     else:
#         return ''



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
        # csvCombine(input_dir, temp_dir)
        return [html.Li(file_download_link(filename)) for filename in files]


if __name__ == '__main__':
    app.run_server(debug=True)