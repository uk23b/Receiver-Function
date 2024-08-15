# This script will update the ray parameter file to have the same period as the dispersion file.
import sys
import os
import numpy as np
import scipy.io as sio
import mat73 as mat
import pandas as pd




# main path that contains all the dispersion files
main_path = '/Users/utkukocum/Desktop/RF_Surf/final25_good/CCPDATA_dilate/'

# list of bin files
bin_files = os.listdir(main_path)

print(bin_files)

# read ccp_stacks_azerbaijan.txt file with pandas

ccp_stacks = pd.read_csv(main_path + 'ccp_stacks_25_good_5.txt', sep='\s+', header=None)
print(ccp_stacks)


#  read ray_param.txt file with pandas
ray_param = pd.read_csv(main_path + 'ray_param_updated_hit5.txt', sep='\s+', header=None)
print(ray_param)

#match lat (column 1) and lon (column 2) from ray_param.txt with lat (column 2) and lon (column 1) from ccp_stacks_azerbaijan.txt ...
# and add ray parameter (column 3) from ray_param.txt to ccp_stacks_azerbaijan.txt for each matchin pair of lat and lon

# empty list
ray_param_coords = []
for i in range(len(ray_param)):
    lati = ray_param.iloc[i,0]
    loni = ray_param.iloc[i,1]
    #print(lati, loni)
    ray_param_coords.append([lati, loni])

    # update the ray_param lati by -0.05 degrees
    print(lati, loni)


for j in range(len(ccp_stacks)):
    latj = ccp_stacks.iloc[j,1]
    lonj = ccp_stacks.iloc[j,0]
    print(latj, lonj)
    if [latj, lonj] in ray_param_coords:
        print('found')
        ray_param_index = ray_param_coords.index([latj, lonj])
        ray_param_value = ray_param.iloc[ray_param_index,2]
        print(ray_param_value)
        # # add new column to ccp_stacks_azerbaijan.txt
        # ccp_stacks['ray_param'] = ray_param_value
        # update the last column of ccp_stacks_azerbaijan.txt with ray_param_value (with 4 floating points)
        ccp_stacks.iloc[j,-1] = '{:.4f}'.format(ray_param_value)
        # update lon of ccp_stacks_azerbaijan.txt with lonj, shift by -0.05 degrees
        #ccp_stacks.iloc[j,0] = '{:.4f}'.format(lonj - 0.05)
        ccp_stacks.iloc[j,0] = '{:.4f}'.format(lonj)
        # latitude will be shifted from for example 43.125 to 43.100
        #ccp_stacks.iloc[j,1] = '{:.4f}'.format(latj - 0.025)
        ccp_stacks.iloc[j,1] = '{:.4f}'.format(latj)
        
        

# format all the columns with 4 floating points
ccp_stacks = ccp_stacks.applymap(lambda x: '{:.4f}'.format(x) if isinstance(x, float) else x)

print(ccp_stacks)

# write new ccp_stacks_azerbaijan.txt file (with 4 floating points )
np.savetxt(main_path + 'all_good_ray_param_hit5_processed_25.txt', ccp_stacks, fmt='%s', delimiter=' ')

#ccp_stacks.to_csv(main_path + 'ccp_stacks_azerbaijan_ray.txt', sep=' ', header=None, index=None)

    












    

