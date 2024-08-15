# I am going to test joint96 with Herrmann's data combining with my data

import os, sys
import pandas as pd
import pygmt
import numpy as np
import matplotlib.pyplot as plt
import subprocess


infile = './DOIT.deep'
# main working directory
main_path = '/Volumes/LaCie2/17_Hermann/test32/JOINT/'
# work folder
work_folder = 'work_joint_scratch'



# create a 'work_joint_scratch' directory if not exists
if not os.path.exists(os.path.join(main_path, work_folder)):
    os.makedirs(os.path.join(main_path, work_folder))

print('work folder created')

# change current working directory to main_path+work_folder
os.chdir(os.path.join(main_path, work_folder))

# copy dispersion data to work folder
dispersion_file = 'nnall.dsp'

# read .sac files under the 'work_joint_scratch' directory

work_folder_path = os.path.join(main_path, work_folder)
files = os.listdir(work_folder_path)
sac_files = [file for file in files if file.endswith('.sac')]
print(sac_files)

# create rftn.lst file
rftn_lst = 'rftn.lst'
with open(rftn_lst, 'w') as f:
    for file in sac_files:
        f.write(file +'\n')

f.close()

jt_out_file = 'joint.out'
f5 = open(work_folder_path +  jt_out_file, 'w')

subprocess.call(infile, stdout=f5)
f5.close()
#subprocess.call(infile_2, stdout=f5)