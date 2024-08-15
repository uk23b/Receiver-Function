# This script removes duplicate entries from the dispersion file contents and sort rows by period(the previous of last column) in ascending order.

import sys
import os
import numpy as np

input_period_list = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,50,67,80,100,111,143]

#input_period_list = [8,10,12,14,16,18,20,22,25,29,33,36,40,50]

error = 0.005

# main path that contains all the dispersion files
main_path = '/Volumes/UNTITLE/16_Jonathan/test6/dispersion_output/'

# list of dispersion files
disp_files = os.listdir(main_path)

organize =[]

# loop over dispersion files
for disp_file in disp_files:
    # clear organize list
    organize =[]
    # read dispersion file by open it
    # skip file that starts with '.'
    if disp_file[0] == '.':
        continue

    print(disp_file)
    f = open(main_path + disp_file, 'r') 
    # read all lines in the file
    lines = f.readlines()
    # remove duplicate lines
    lines = list(set(lines))
    # loop over lines
    for line in lines:
        # split line by space
        line = line.split()
        # convert to float
        line = [str(i) for i in line]
        # append to organize list
        organize.append(line)
    # convert 6th column to float
    organize = np.array(organize)

    
    # sort organize list by period in ascending order (6th column of each row)
    organize = sorted(organize, key=lambda x: float(x[5]))
    print(organize)

    # select only the rows that have period in input_period_list
    organize = [i for i in organize if float(i[5]) in input_period_list]


    # write to file with np.savetxt
    np.savetxt(main_path + disp_file, organize, fmt='%s', delimiter=' ')

    f.close()
    








    

