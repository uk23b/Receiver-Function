import os
import numpy as np
import pygmt
import xarray as xr
from scipy import stats
import re
from os.path import abspath
import subprocess


# Define the paths and parameters
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)
region = [36, 52, 35, 45.5]  # Define region as lon_min, lon_max, lat_min, lat_max
vel_path = '/Users/utkukocum/Desktop/RF_Surf/final25/TPWT_2/'
plots_path = os.path.join(vel_path, 'plots')
os.makedirs(plots_path, exist_ok=True)

# List of depths for grid files
depths = ['40', '60', '80', '100']
topo_data = '@earth_relief_30s'  # 30 arc second global relief

# Function to convert grd files to xyz, read xyz to numpy, and find z differences
def process_grid_files(base_depth, compare_depths):
    base_file_path = os.path.join(vel_path, f'gridvel.007.22.80.1_{base_depth}km.grd')
    base_data = read_xyz_data(base_file_path)

    for depth in compare_depths:
        compare_file_path = os.path.join(vel_path, f'gridvel.007.22.80.1_{depth}km.grd')
        compare_data = read_xyz_data(compare_file_path)
        diff = find_z_diffs(base_data, compare_data)
        diff_path = os.path.join(plots_path, f'diff_{base_depth}_{depth}.xyz')
        np.savetxt(diff_path, diff, fmt='%.6f')
        convert_to_grd_and_plot(diff_path, base_depth, depth)

# Read xyz data into numpy arrays
def read_xyz_data(grd_path):
    xyz_path = os.path.splitext(grd_path)[0] + '.xyz'
    os.system(f'gmt grd2xyz {grd_path} > {xyz_path}')
    return np.loadtxt(xyz_path, dtype=float)

# Find z differences
def find_z_diffs(data1, data2):
    assert np.array_equal(data1[:, :2], data2[:, :2]), "Coordinates do not match."
    z_diffs = data1[:, 2] - data2[:, 2]
    return np.column_stack((data1[:, :2], z_diffs))

# Convert xyz to grd and plot
def convert_to_grd_and_plot(xyz_path, base_depth, compare_depth):
    grd_path = xyz_path.replace('.xyz', '.grd')
    os.system(f'gmt xyz2grd {xyz_path} -G{grd_path} -R{region[0]}/{region[1]}/{region[2]}/{region[3]} -I0.1')
    plot_grid(grd_path, base_depth, compare_depth)

# Plot grid function
def plot_grid(grd_path, base_depth, compare_depth):

    #period = extract_period(grd_file)

    #fig.coast(shorelines=True, borders=[1, 2], region=region, projection="M8i", frame=True)
    fa_path = abspath("./plots_fault/me_faults.car")
    s1="awk '{print $2,$1}' ./plots/me_faults.car > ./plots_fault/me_reversed.car"
    s2="awk '{print $2,$1}' ./plots/me_reversed.car > ./plots_fault/me_reversed_2.car"
    s1_call=subprocess.call(s1, shell=True)
    s2_call=subprocess.call(s2, shell=True)

    f_path = abspath("./plots_fault/OBSsta.txt")
    file=open(f_path)
    lines=file.readlines()

    staname_list=[]
    stalat_list=[]
    stalon_list=[]

    for ii in lines:
        #print(ii)
        isiplit=ii.split("\t")
        sta_name=isiplit[0]
        sta_lat=float(isiplit[2])
        sta_lon=float(isiplit[3])
        staname_list.append(sta_name)
        stalat_list.append(sta_lat)
        stalon_list.append(sta_lon)

    fig = pygmt.Figure()
    fig.basemap(region=region, projection="M8i", frame=True)
        # with minimum and maximum values -2000 to 5000 meter
    pygmt.makecpt(cmap="gray", series=[-2000, 7000])
    fig.grdimage(grid=topo_data, region=region, projection="M8i",  frame=True, shading=True)
    cpt_file = "custom_seis.cpt"
    stats = calculate_statistics(grd_path)
    mini = -0.1
    maxi = 0.1
    interi = (maxi - mini)/10
    pygmt.makecpt(series=[mini, maxi, interi], cmap='seis', continuous=False, output=cpt_file)
    #pygmt.makecpt(series=[stats['min_val'], stats['max_val'], (stats['max_val'] - stats['min_val'])/10], cmap='seis', continuous=False, output=cpt_file)
    fig.grdimage(grid=grd_path, region=region, projection="M8i", frame=True, cmap=cpt_file, t=60)
    fig.colorbar(cmap=cpt_file, frame='af+l"c (km/s)"')



    # # Enhanced coastlines, shorelines, and borders
    # #fig.grdimage(grid=grd_file_path, cmap=True, region=region, projection="M6i", frame=True, t=10)
    fig.coast(shorelines=True, borders=[1, 2], region=region, projection="M8i", frame=True)

    fig.plot(x=stalon_list, y=stalat_list,style="t0.2c",color='gray',
                 pen="black")

    #read fault file
    fa_path = abspath("./plots_fault/me_faults.car")
    file2=open(fa_path)
    lines2=file2.readlines()

    numbers = []

    falat_list_m=[]
    falon_list_m=[]

    falat_list=[]
    falon_list=[]

    for j in lines2:
        jsplit=j.split("\n")
        jsplit = list(filter(None, jsplit))
        if 'SEGMENT' in j:
            falat_list.clear()
            falon_list.clear()
        for word in jsplit:
            #print(type(word))
            xa=re.findall('[0-9]+',word)
            #print(word)
            if len(xa)!=0:
                #print((xa))
                x=xa[0]+'.'+xa[1]
                y=xa[2]+'.'+xa[3]
                x1=float(x)
                y1=float(y)
                #print(x,y)
                falat_list.append(float(x1))
                falon_list.append(float(y1))
            print(falat_list)
    #fig.plot(x=falat_list, y=falon_list ,pen="1,red")

    with open('./plots_fault/me_reversed_2.car', "r") as f:
        lines = f.readlines()
    with open('./plots_fault/me_reversed_3.car', "w") as f:
        for line in lines:
            if line.strip("\n") != " SEGMENT":
                f.write(line)
            if "SEGMENT" in line:
                f.write(">")
    #fig.plot(data='rays.dat',pen="0.1,black")
    fig.plot(data='./plots_fault/me_reversed_3.car',pen="0.6,gray")
    fig.plot(data='./plots_fault/cauc_actflt.gmt',pen="0.6,gray")

    fig.savefig(os.path.join(plots_path, f'diff_{base_depth}_{compare_depth}.png'))

# Calculate statistics of grid data
def calculate_statistics(grd_file_path):
    data = xr.open_dataarray(grd_file_path).values.flatten()
    data = data[~np.isnan(data)]
    return {
        'mean': np.mean(data),
        'mode': stats.mode(data)[0][0],
        'variance': np.var(data),
        'max_val': np.max(data),
        'min_val': np.min(data)
    }

# Main execution loop
for i in range(len(depths) - 1):
    base_depth = depths[i]
    compare_depths = depths[i + 1:]
    process_grid_files(base_depth, compare_depths)
