# create sac file list
import os, sys
import numpy as np
import subprocess

# main path that contains all the receiver function files
main_path = '/Users/utkukocum/Desktop/RF_Surf/final25/CCPtoRFs/'

output_path = '/Users/utkukocum/Desktop/RF_Surf/final25/'

# list of receiver function files
rec_files = os.listdir(main_path)
print(rec_files)
# get only .sac files
rec_files = [file for file in rec_files if file.endswith('.sac')]
rec_files.sort()

# create output file
f = open(main_path + 'rec_func_list.txt', 'w')

# loop over receiver function files
for rec_file in rec_files:
    # skip file that starts with '.'
    if rec_file[0] == '.':
        continue
    print(rec_file)
    # write name of the file to output file
    f.write(rec_file + '\n')

f.close()

# move output file to output path
subprocess.call(['mv', main_path + 'rec_func_list.txt', output_path])


    

