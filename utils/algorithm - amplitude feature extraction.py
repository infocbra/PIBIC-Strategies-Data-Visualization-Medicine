# -*- coding: utf-8 -*-
"""feature extraction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jlwDP6v2Te9F1l-qB26fkhngcfAO70dK

# 1. Preparation of Dataset to feature extraction
"""

from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import math

# load the features table
features_df = pd.read_csv('/content/drive/My Drive/Projects/PIBIC - Estratégia para visualização de dados/Feature extraction/features_extracted.csv')
# features_df.drop(['Unnamed: 0'],inplace=True)

subject_id=10
sensor = 1 # 1 - gyro ; 2 - NCC
parkinsonian = 1 # 0 - without parkinson ; 1 - with parkinson
axis = 2 # 1- X ; 2 - Y ; 3 - Z
repetition = 1 # set of data (repetition)

# location of subjects 10 dataframe

link = 'Feature extraction/rubens_01_r.csv' #rubens01
# link = 'Feature extraction/rubens_02_r.csv' #rubens02
# link = 'Feature extraction/rubens_03_r.csv' #rubens03
# link = 'Feature extraction/aparecido_01_r.csv' #aparecido01
# link = 'Feature extraction/aparecido_02_r.csv' #aparecido02
# link = 'Feature extraction/aparecido_03_r.csv' #aparecido03

subj_df = pd.read_csv('/content/drive/My Drive/Projects/PIBIC - Estratégia para visualização de dados/'+link)
# subj_df['audio_signal']=subj_df['audio_signal'].fillna(-1)

subj_df.head(1)

index_ini_fim_tasks = subj_df.loc[subj_df['audio_signal']==0].index

tuple_between = []
for i in range(0,len(index_ini_fim_tasks)-1):
        tuple_between.append((index_ini_fim_tasks[i],index_ini_fim_tasks[i+1]))
        aux = index_ini_fim_tasks[i+1]

tuple_between

"""# 2. Features:

## MAV
Median absolute value
"""

def get_mav(dataframe):
    return (dataframe.abs().sum())/(len(dataframe))

"""## RMS
Root median square
"""

def get_rms(arr,n):
    square = 0
    mean = 0.0
    root = 0.0

    #square
    for i in range(0,n):
        square+=(arr[i]**2)
    #mean
    mean = (square/(float)(n))
    #root
    root = math.sqrt(mean)

    return root

"""## Peak
maximum value & index of it
"""

def get_peak(arr):
    max = arr.max()
    # for i in arr.index:
    #     if arr[i]==max:
    #         index=i
    return max#,index

"""## MAVSDN
mean absolute value of the second diferences normalized<br>
Code based in [THIS](https://github.com/UlysseCoteAllard/sEMG_handCraftedVsLearnedFeatures/blob/a935b31774407fb823714a672dfd713322a8371c/PrepareAndLoadData/feature_extraction.py)
"""

def get_mavsdn(vector):
    # N = len(arr)
    # acum = 0
    # std = arr.std()
    # mean = arr.mean()
    # arr_norm = (arr-mean)/std

    # for i in range(0,N-2):
    #     acum+= np.abs((arr_norm[i+2]-arr_norm[i]))
    # return ((1/(N/2))*acum)
    vector = np.asarray(vector)
    std = np.std(vector)
    return np.mean(np.abs(np.diff(np.diff(vector))))/std

"""## MAVSD
mean absolute value of the second diferences<br>
Code based in [THIS](https://github.com/UlysseCoteAllard/sEMG_handCraftedVsLearnedFeatures/blob/a935b31774407fb823714a672dfd713322a8371c/PrepareAndLoadData/feature_extraction.py)
"""

def get_mavsd(vector):
    vector = np.asarray(vector)
    return np.mean(np.abs(np.diff(np.diff(vector))))

"""## MAVFDN
mean absolute value of first difference normalized<br>
Code based in [THIS](https://github.com/UlysseCoteAllard/sEMG_handCraftedVsLearnedFeatures/blob/a935b31774407fb823714a672dfd713322a8371c/PrepareAndLoadData/feature_extraction.py)
"""

def get_mavfdn(vector):
    vector = np.asarray(vector)
    std = np.std(vector)
    return np.mean(np.abs(np.diff(vector)))/std

"""## STD
standard deviation
"""

def get_std(vector):
    return vector.std()

"""# Task 1:


> remember we are not using the first task itself because is so close to the second one.

So our first interval is from 654 to 1154
"""

task  = 1 # actually the second in the original DF

start,end = tuple_between[1]

tsk1_df = subj_df[(subj_df.index>=start) & (subj_df.index<end)]

"""## Getting Y axis of gyro"""

# get a series of data
tsk1y_df = tsk1_df['G1Y']

# median absolute value
mav = get_mav(tsk1y_df)

# root mean square
rms = get_rms(tsk1y_df.to_numpy(),len(tsk1y_df))

#peak
peak = get_peak(tsk1y_df)

#mavsdn
mavsdn = get_mavsdn(tsk1y_df)

#mavsd
mavsd = get_mavsd(tsk1y_df)

#mavfdn
mavfdn = get_mavfdn(tsk1y_df)

#std
std=get_std(tsk1y_df)

peak

features_df.head()

row = pd.Series([subject_id,repetition,task,sensor,axis,parkinsonian,mav,rms,peak,mavsdn,mavsd,mavfdn,std],index=features_df.columns)

row

features_df = features_df.append(row, ignore_index=True)

"""## Getting Z axis of gyro"""

# get a series of data
tsk1z_df = tsk1_df['G1Z']

# Features
mav = get_mav(tsk1z_df)
rms = get_rms(tsk1z_df.to_numpy(),len(tsk1z_df))
peak = get_peak(tsk1z_df)
mavsdn = get_mavsdn(tsk1z_df)
mavsd = get_mavsd(tsk1z_df)
mavfdn = get_mavfdn(tsk1z_df)
std=get_std(tsk1z_df)

axis = 3 #indicates the Z axis

# Row of features
row = pd.Series([subject_id,repetition,task,sensor,axis,parkinsonian,mav,rms,peak,mavsdn,mavsd,mavfdn,std],index=features_df.columns)

# Add to DF
features_df = features_df.append(row, ignore_index=True)

"""# Tasks from 3 to 9"""

# tuple_between = [(154, 654),(654,1154), (1154, 1754),(1754, 2354), (2354,2954), (2954,3554), (3554,4204), (4204,4854), (4854,5504), (5504,6154)]

for i in range (2,10):
    task = i
    start,end = tuple_between[i]
    tsk_df = subj_df[(subj_df.index>=start) & (subj_df.index<end)]

    # gyro Y extraction
    axis=2
    tsky_df = tsk_df['G1Y'] # get a series of data
    mav = get_mav(tsky_df)
    rms = get_rms(tsky_df.to_numpy(),len(tsky_df))
    peak = get_peak(tsky_df)
    mavsdn = get_mavsdn(tsky_df)
    mavsd = get_mavsd(tsky_df)
    mavfdn = get_mavfdn(tsky_df)
    std=get_std(tsky_df)

    row = pd.Series([subject_id,repetition,task,\
                     sensor,axis,parkinsonian,mav,rms,peak,mavsdn,\
                     mavsd,mavfdn,std],index=features_df.columns)
    
    features_df = features_df.append(row, ignore_index=True)

    # gyro Z extraction
    axis=3
    tsky_df = tsk_df['G1Z'] # get a series of data
    mav = get_mav(tsky_df)
    rms = get_rms(tsky_df.to_numpy(),len(tsky_df))
    peak = get_peak(tsky_df)
    mavsdn = get_mavsdn(tsky_df)
    mavsd = get_mavsd(tsky_df)
    mavfdn = get_mavfdn(tsky_df)
    std=get_std(tsky_df)

    row = pd.Series([subject_id,repetition,task,\
                     sensor,axis,parkinsonian,mav,rms,peak,mavsdn,\
                     mavsd,mavfdn,std],index=features_df.columns)
    
    features_df = features_df.append(row, ignore_index=True)

"""# Save to File"""

features_df

features_df.to_csv('/content/drive/My Drive/Projects/PIBIC - Estratégia para visualização de dados/Feature extraction/features_extracted.csv',index=False)