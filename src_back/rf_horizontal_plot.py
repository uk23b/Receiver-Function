# this is a plotiing script for S wave velocity structure.

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os, sys
import pygmt

topo_data = '@earth_relief_30s' #30 arc second global relief (SRTM15+V2.1 @ 1.0 km)

# source file folder
source_folder = '/Volumes/UNTITLE/17_Hermann/test32/JOINT/work/receiver_function_inversion/'

# output file folder
output_folder = '/Volumes/UNTITLE/17_Hermann/test32/JOINT/work/receiver_function_inversion/plotting'

# if output folder does not exist, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# list of source files
source_files = os.listdir(source_folder)

# loop over source files
all_info = []
for source_file in source_files:
    # skip file that starts with '.'
    if source_file[0] == '.':
        continue
    # read source file ends with only .o 
    source_path = source_folder + '/' + source_file
    all_lines = []
    # if source file ends with .txt



    if source_file[-4:] == '.txt':
        # print(source_path)
        # read the txt file with pandas
        df = pd.read_csv(source_path, engine='python', encoding='cp1252', header=None)
        # skip the first 300 lines
        df = df.iloc[377:]
        # print(df)
        # write 
        file = source_file.split('_')
        print(file)
        fs1 = file[0].split('.')
        fs2 = file[1].split('.')
        lon = float(fs1[1] + '.' + fs1[2])
        lat = float(fs2[0] + '.' + fs2[1])
        print(lon, lat)
        #print(df)
        # first row is depth
        line = df.iloc[:, 0].values
        #print(depth)
        depth_vp_vs = []
        cumulative_depth_vp_vs = []
        for i in range(len(line)):
            #print('depth is ,' ,line[i])
            # first value is depth of i is depth
            # split the line
            line_split = line[i].split(' ')
            #print(line_split)
            # remove empty string
            line_split = [i for i in line_split if i != '']
            #print(line_split)
            lay = float(line_split[0])
            depth = float(line_split[1])
            vs = float(line_split[2])
            #print(depth, vs)
            #all_info.append([ float(depth), float(lay), float(vs), float(longitude), float(latitude)])
            depth_vp_vs.append([depth, lay, vs])
                # cumulative depth = depth + previous cumulative depth
            if len(cumulative_depth_vp_vs) == 0:
                cumulative_depth_vp_vs.append([depth, lay, vs])
            else:
                previous_cumulative_depth = cumulative_depth_vp_vs[-1][0]
                cumulative_depth = depth + previous_cumulative_depth
                cumulative_depth_vp_vs.append([cumulative_depth, lay, vs, lon, lat])
                all_info.append([cumulative_depth, lay, vs, lon, lat])

# from all_info, sort by depth if not 190 
all_info = [i for i in all_info if i[0] != 190.0]
all_info = sorted(all_info, key=lambda x: x[0])

# filter by certain depth, lets say 100

target_depth = 17.0

all_info = [i for i in all_info if i[0] == target_depth]
print(all_info)

output_S_grd = '{}km.grd'.format(target_depth)
output_S_grd = os.path.join(output_folder, output_S_grd)

# find max and min of lon and lat
lon_min = min([i[3] for i in all_info])
lon_max = max([i[3] for i in all_info])
lat_min = min([i[4] for i in all_info])
lat_max = max([i[4] for i in all_info])


#max_lon = 52.0
max_lon = 50.15
#min_lon = 36.5
min_lon = 42.0
#max_lat = 44.5
max_lat = 43.5
#min_lat = 35.5
min_lat = 38.0

#find max and min of S velocity
#S_min = min([i[2] for i in all_info])
#S_max = max([i[2] for i in all_info])

S_min = 2
S_max = 5

# first column is lon, second column is lat, third column is S, write to file
output_S = '{}km.txt'.format(target_depth)
output_S = os.path.join(output_folder, output_S)
# only write lon, lat, S velocity row by row to file
with open(output_S, 'w') as f:
    for row in all_info:
        lon = row[3]
        lat = row[4]
        S = row[2]
        f.write('{} {} {}\n'.format(lon, lat, S))



command = 'gmt xyz2grd {} -R{}/{}/{}/{} -I0.1d -G{}'.format(output_S, lon_min, lon_max, lat_min, lat_max, output_S_grd)
print(command)
os.system(command)


interval = 0.001
fig = pygmt.Figure()
title_str = '+t" Depth = {} km "'.format(target_depth)
fig.basemap(region=[min_lon, max_lon, min_lat, max_lat], projection="M8i", frame=["a", title_str])
fig.grdimage(grid=topo_data,C='gray')
pygmt.makecpt(series=[S_min,S_max,interval], cmap="seis",continuous='True')
fig.grdimage(grid=output_S_grd, t= 60)
fig.colorbar(frame='+l" "',position="x21.5c/18.0c+w18c+jTC+v")
fig.coast(shorelines=True)
fig.show()

# save figure
output_fig = '{}km.png'.format(target_depth)
output_fig = os.path.join(output_folder, output_fig)
fig.savefig(output_fig)

