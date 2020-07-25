# H1B and PERM prediction

An app to predict CONFIRM/DENIED for the H1B and PERM application.

### To run the app

1. create virtual environment  
virtualenv -p python3.7 venv
2. install packages  
pip install -r conf/requirements.txt
3. spin on app  
python index.py

#### Note

In the directory dialog, the path should be a folder, e.g. /user/.
* the training data for H1B will be kept in /user/input_h1b
* the training data for PERM will be kept in /user/input_perm
* the discription for for training data will be kept in /user/header, naming headers.csv and PERMheaders.csv
* the prediction data will be kept in /user/predict
* the code will be in /user/h1permprediction
* the model will be in /user/model
* the temprory files will be in /user/temp
* the output, model and temporary folder will be generated during execution under base diretory.