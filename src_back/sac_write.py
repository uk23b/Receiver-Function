import os,sys
import numpy as np
import pandas as pd
import subprocess
import obspy


rftn = '2.5'
gauss = '2.5'

target_freq = 10

# output_file 
out_file = 'output_fit.txt'

# main path that contains all the raw data.
main_folder = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/All_1/'
main_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/All_1/done1/'
f = open(main_path + '/' + out_file, 'a')

# list folders
folders = os.listdir(main_path)

# list only folders in the main path
folders = [folder for folder in folders if os.path.isdir(main_path + folder)]

# sort folders
folders.sort()

# list only the folders start with 'Event'
subfolders = [f.name for f in os.scandir(main_path) if f.is_dir() and f.name.startswith('Event')]
print(subfolders)
# sort subfolders
subfolders.sort()
# loop over subfolders
for folder in subfolders:
    # list files in the folder
    files = os.listdir(os.path.join(main_path, folder))
    print(files)
    # loop over files
    for file in files:
        # if file is a SAC file
        if file.endswith('.SAC'):
            # read sac file
            source_sac_path = main_path + folder + '/' + file
            target_sac_path = main_folder + 'GOOD_DATA/' + folder + '/' + file
            st = obspy.read(source_sac_path)
            # decimate the data
            dec_rate = st[0].stats.sampling_rate / target_freq
            if st[0].stats.sampling_rate == 200:
                dec_rate = 20
                st.decimate(10)
                st.decimate(2)
            else:
                print(dec_rate)
                dec_rate = int(dec_rate)
                # decimate
                st.decimate(dec_rate)
                print(st)
                print(st[0].stats.sampling_rate)
                # write to the GOOD DATA FOLDER
            st.write(target_sac_path, format='SAC')
                #subprocess.call(['cp', source_sac_path, target_sac_path])
            st.clear()