import os, sys
import shutil
import obspy
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import glob

source_path = r'/Volumes/UNTITLE/10_cft_snr/'
file = 'main_stalta.txt'

target_freq = 10

# read the file
df = pd.read_csv(os.path.join(source_path, file), sep=' ', header=None)


event_data = df.iloc[:,0]
snr = df.iloc[:,1]
mag = df.iloc[:,2]
ray_param = df.iloc[:,3]
incidence = df.iloc[:,4]
distance = df.iloc[:,5]

# add new column to df

# label the data based on snr, 
# if snr>3, label = good
# if snr<3 and snr>2, label = ok_good
# if snr<2 and snr>1, label = ok_bad
# if snr<1, label = bad
#append label to df

for i in range(len(event_data)):
    if snr[i] > 3:
        label = 'good'
        df.loc[i, 'label'] = label
        # change "UNTITLED" to "UNTITLE" in event_data
        event_data[i] = event_data[i].replace('UNTITLED', 'UNTITLE')
    elif snr[i] < 3 and snr[i] > 2.5:
        label = 'ok_good'
        df.loc[i, 'label'] = label
        # change "UNTITLED" to "UNTITLE" in event_data
        event_data[i] = event_data[i].replace('UNTITLED', 'UNTITLE')
        #print(event_data[i])
    elif snr[i] < 2.5 and snr[i] > 1.5:
        label = 'ok_ok'
        df.loc[i, 'label'] = label
        # change "UNTITLED" to "UNTITLE" in event_data
        event_data[i] = event_data[i].replace('UNTITLED', 'UNTITLE')
    elif snr[i] < 1.5 and snr[i] > 1.0:
        label = 'ok_bad'
        df.loc[i, 'label'] = label
        # change "UNTITLED" to "UNTITLE" in event_data
        event_data[i] = event_data[i].replace('UNTITLED', 'UNTITLE')
    elif snr[i] < 1:
        label = 'bad'
        df.loc[i, 'label'] = label
        # change "UNTITLED" to "UNTITLE" in event_data
        event_data[i] = event_data[i].replace('UNTITLED', 'UNTITLE')


# save the df to a new file
df.to_csv(os.path.join(source_path, 'main_stalta_labelled.txt'), sep=' ', header=None, index=None)


        











