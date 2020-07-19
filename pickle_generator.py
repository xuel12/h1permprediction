import pandas as pd
import pickle
import constants
from constants import job_level_map, US_STATE_ABBREV, PW_WAGE_LEVEL_MAP, SOC_MAP, unit_map
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from imblearn.over_sampling import SMOTE



temp_dir = constants.TEMP_DIR
def jobClassifier(soc_code, SOC_MAP):
    soc_map = SOC_MAP
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

def PERMmodel():
    csvfile = 'PERM_2020.csv'
    perm20 = pd.read_csv(temp_dir + csvfile, engine='python')
    perm20 = perm20.fillna("Unknown")
    select_columns = [
        'CASE_STATUS',
        'REFILE',
        'WORKSITE_STATE',
        'FW_OWNERSHIP_INTEREST',
        'PW_SKILL_LEVEL',
        'MINIMUM_EDUCATION',
        'REQUIRED_TRAINING',
        'ACCEPT_ALT_FIELD_OF_STUDY',
        'JOB_OPP_REQUIREMENTS_NORMAL',
        'FOREIGN_LANGUAGE_REQUIRED',
        'PROFESSIONAL_OCCUPATION',
        'APP_FOR_COLLEGE_U_TEACHER',
        'FOREIGN_WORKER_BIRTH_COUNTRY',
        'CLASS_OF_ADMISSION',
        'FOREIGN_WORKER_TRAINING_COMP'
    ]
    perm20 = perm20[(perm20['CASE_STATUS'].str.upper() == 'CERTIFIED') | \
                    (perm20['CASE_STATUS'].str.upper() == 'DENIED')]
    perm20["WORKSITE_STATE"] = perm20["WORKSITE_STATE"].map(US_STATE_ABBREV)
    perm20 = perm20[select_columns]
    cate_column_name = [
        'REFILE',
        'WORKSITE_STATE',
        'FW_OWNERSHIP_INTEREST',
        'PW_SKILL_LEVEL',
        'MINIMUM_EDUCATION',
        'REQUIRED_TRAINING',
        'ACCEPT_ALT_FIELD_OF_STUDY',
        'JOB_OPP_REQUIREMENTS_NORMAL',
        'FOREIGN_LANGUAGE_REQUIRED',
        'PROFESSIONAL_OCCUPATION',
        'APP_FOR_COLLEGE_U_TEACHER',
        'FOREIGN_WORKER_BIRTH_COUNTRY',
        'CLASS_OF_ADMISSION',
        'FOREIGN_WORKER_TRAINING_COMP']
    data = pd.get_dummies(perm20, columns=cate_column_name)
    data = data.reset_index(drop=True)

    X_train = data.drop(['CASE_STATUS'], axis=1)
    y_train = data['CASE_STATUS']

    oversample = SMOTE()
    x_train_n, y_train_n = oversample.fit_resample(X_train, y_train)
    rfc = RandomForestClassifier(n_estimators=100, bootstrap=True, criterion='gini', oob_score=True)
    rfc.fit(x_train_n, y_train_n)

    pickle_out = open(temp_dir + "PERM_RF_MODEL_2020.pickle", "wb")
    pickle.dump(rfc, pickle_out)
    pickle_out.close()


def H1Bmodel():
    csvfile = 'H1B_2020.csv'
    H1B20 = pd.read_csv(temp_dir + csvfile, engine='python')
    H1B20 = H1B20[((H1B20['CASE_STATUS'].str.upper() == 'CERTIFIED') | \
                               (H1B20['CASE_STATUS'].str.upper() == 'DENIED')) & \
                              (H1B20['VISA_CLASS'].str.upper() == 'H-1B')]
    H1B20 = H1B20[H1B20.EMPLOYER_COUNTRY == 'UNITED STATES OF AMERICA']
    H1B20['JOB_CATEGORY']=H1B20['SOC_CODE'].apply(lambda x: jobClassifier(x, SOC_MAP))
    H1B20['JOB_LEVEL']=H1B20['JOB_TITLE'].apply(lambda x: levelClassifier(x))
    H1B20["PW_WAGE_LEVEL"] = H1B20["PW_WAGE_LEVEL"].map(PW_WAGE_LEVEL_MAP)
    H1B20['PW_WAGE_LEVEL'] = H1B20['PW_WAGE_LEVEL'].fillna("UNKNOWN")
    H1B20["WORKSITE_STATE"] = H1B20["WORKSITE_STATE"].map(US_STATE_ABBREV)
    H1B20["EMPLOYER_STATE"] = H1B20["EMPLOYER_STATE"].map(US_STATE_ABBREV)
    H1B20["PW_UNIT_OF_PAY"] = H1B20["PW_UNIT_OF_PAY"].map(unit_map)
    selected_variables = ['CASE_STATUS',
                          'EMPLOYER_STATE',
                          'WORKSITE_STATE',
                          'JOB_CATEGORY',
                          'JOB_LEVEL',
                          'FULL_TIME_POSITION',
                          'PW_UNIT_OF_PAY',
                          'PW_WAGE_LEVEL',
                          'H-1B_DEPENDENT',
                          'WILLFUL_VIOLATOR']
    H1B20 = H1B20[selected_variables]
    cate_column_name = [
        'EMPLOYER_STATE',
        'WORKSITE_STATE',
        'JOB_CATEGORY',
        'JOB_LEVEL',
        'FULL_TIME_POSITION',
        'PW_UNIT_OF_PAY',
        'PW_WAGE_LEVEL'
        , 'H-1B_DEPENDENT',
        'WILLFUL_VIOLATOR']
    data20 = pd.get_dummies(H1B20, columns=cate_column_name)
    data20 = data20.reset_index(drop=True)
    oversample = SMOTE()
    X_train20 = data20.drop(['CASE_STATUS'], axis=1)
    y_train20 = data20['CASE_STATUS']
    X_train_res, y_train_res = oversample.fit_resample(X_train20, y_train20)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_res, y_train_res)

    pickle_out = open(temp_dir + "H1B_LR_MODEL_2020.pickle", "wb")
    pickle.dump(model, pickle_out)
    pickle_out.close()


def PERMeda():
    csvfile = 'perm2015to2019_sub.csv'
    perm = pd.read_csv(temp_dir + csvfile, engine='python')
    perm = perm.fillna("Unknown")
    perm["JOB_INFO_WORK_STATE"] = perm["JOB_INFO_WORK_STATE"].map(US_STATE_ABBREV)
    perm["EMPLOYER_STATE"] = perm["EMPLOYER_STATE"].map(US_STATE_ABBREV)
    perm['countvar'] = 1
    perm = perm.replace('Certified', 'CERTIFIED')
    perm = perm.replace('Denied', 'DENIED')

    edaplot = {}
    edaplot['CASE_STATUS'] = perm.groupby('CASE_STATUS').count()
    edaplot['EMPLOYER_STATE'] = perm.groupby('EMPLOYER_STATE').count()
    edaplot['WORKSITE_STATE'] = perm.groupby('JOB_INFO_WORK_STATE').count()
    edaplot['PW_WAGE_LEVEL'] = perm.groupby(['PW_LEVEL_9089', 'CASE_STATUS'], as_index=False).count()
    edaplot['REFILE'] = perm.groupby(['REFILE', 'CASE_STATUS'], as_index=False).count()
    edaplot['EDUCATION'] = perm.groupby(['FOREIGN_WORKER_INFO_EDUCATION', 'CASE_STATUS'], as_index=False).count()
    edaplot['JOB_INFO_ALT_FIELD'] = perm.groupby(['JOB_INFO_ALT_FIELD', 'CASE_STATUS'], as_index=False).count()
    dftop = perm.groupby('FW_INFO_BIRTH_COUNTRY', as_index=False).count()
    dftop = dftop.sort_values('countvar', ascending=False)[['FW_INFO_BIRTH_COUNTRY', 'countvar']][0:6]
    edaplot['FW_INFO_BIRTH_COUNTRY'] = perm.groupby(['FW_INFO_BIRTH_COUNTRY', 'CASE_STATUS'], as_index=False).count()
    edaplot['FW_INFO_BIRTH_COUNTRY'] = edaplot['FW_INFO_BIRTH_COUNTRY'][
        edaplot['FW_INFO_BIRTH_COUNTRY'].FW_INFO_BIRTH_COUNTRY.isin(dftop.FW_INFO_BIRTH_COUNTRY)]
    dftop2 = perm.groupby('CLASS_OF_ADMISSION', as_index=False).count()
    dftop2 = dftop2.sort_values('countvar', ascending=False)[['CLASS_OF_ADMISSION', 'countvar']][0:6]
    edaplot['CLASS_OF_ADMISSION'] = perm.groupby(['CLASS_OF_ADMISSION', 'CASE_STATUS'], as_index=False).count()
    edaplot['CLASS_OF_ADMISSION'] = edaplot['CLASS_OF_ADMISSION'][
        edaplot['CLASS_OF_ADMISSION'].CLASS_OF_ADMISSION.isin(dftop2.CLASS_OF_ADMISSION)]
    edaplot['FW_INFO_TRAINING_COMP'] = perm.groupby(['FW_INFO_TRAINING_COMP', 'CASE_STATUS'], as_index=False).count()
    edaplot['JOB_INFO_JOB_REQ_NORMAL'] = perm.groupby(['JOB_INFO_JOB_REQ_NORMAL', 'CASE_STATUS'],
                                                      as_index=False).count()

    pickle_out = open(temp_dir + "edaPERM.pickle", "wb")
    pickle.dump(edaplot, pickle_out)
    pickle_out.close()

def H1Beda():
    csvfile = 'h1b2015to2020_sub.csv'
    df = pd.read_csv(temp_dir + csvfile, parse_dates=['CASE_SUBMITTED'])
    df["PW_WAGE_LEVEL"] = df["PW_WAGE_LEVEL"].map(job_level_map)
    df = df.replace('UNKOWN', 'UNKNOWN')
    df['countvar'] = 1

    edaplot = {}
    edaplot['EMPLOYER_STATE'] = df.groupby('EMPLOYER_STATE').count()
    edaplot['WORKSITE_STATE'] = df.groupby('WORKSITE_STATE').count()
    edaplot['JOB_CATEGORY'] = df.groupby('JOB_CATEGORY').count().sort_values(['countvar'], ascending=False)[0:10]
    edaplot['JOB_LEVEL'] = df.groupby(['JOB_LEVEL', 'CASE_STATUS'], as_index=False).count()
    edaplot['FULL_TIME_POSITION'] = df.groupby('FULL_TIME_POSITION').count()
    edaplot['PW_WAGE_LEVEL'] = df.groupby(['PW_WAGE_LEVEL', 'CASE_STATUS'], as_index=False).count()
    edaplot['H-1B_DEPENDENT'] = df.groupby(['H-1B_DEPENDENT', 'CASE_STATUS'], as_index=False).count()
    edaplot['WILLFUL_VIOLATOR'] = df.groupby('WILLFUL_VIOLATOR').count()
    edaplot['CASE_SUBMITTED'] = (df.groupby(['CASE_STATUS', pd.Grouper(key='CASE_SUBMITTED', freq='M')])['JOB_CATEGORY']
                                 .count().reset_index().pivot(index='CASE_SUBMITTED', columns='CASE_STATUS',
                                                              values='JOB_CATEGORY'))

    pickle_out = open(temp_dir + "eda.pickle", "wb")
    pickle.dump(edaplot, pickle_out)
    pickle_out.close()



#H1Beda()
#PERMeda()
#H1Bmodel()
#PERMmodel()
