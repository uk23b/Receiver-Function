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
min_lat, max_lat = 36.5, 45.5
min_lon, max_lon = 36.5, 52
#inter = 0.001
mini = 4.
maxi = 4.3
interi = (maxi - mini)/10
topo_data = '@earth_relief_30s'  # 30 arc second global relief
vel_path = 'your__vel__path'

# Ensure the plots directory exists
plots_path = os.path.join(vel_path, 'plots')
os.makedirs(plots_path, exist_ok=True)

print(vel_path)
files = os.listdir(vel_path)
#print(files)
# vel files are in 'gridvel.007.22.80.1.sa360kern' , 'gridvel.008.22.80.1.sa360kern' .... so basically look for gridvel
vel_files = [file for file in files if 'gridvel' in file]
print(vel_files)

# Function to calculate statistics of grid data
def calculate_statistics(grd_file_path):
    data = xr.open_dataarray(grd_file_path).values.flatten()
    data = data[~np.isnan(data)]  # Filter out NaN values
    statistics = {
        'mean': np.mean(data),
        'mode': stats.mode(data)[0][0],
        'variance': np.var(data),
        'max_val': np.max(data),
        'min_val': np.min(data)
    }
    return statistics


# read the xyz file and return the and remove the most repeated velocity values from the file and convert back to grd file
def xyz2grd(xyz_file_path):
    data = np.genfromtxt(xyz_file_path)
    mode = stats.mode(data[:, 2])[0][0]
    #data = data[data[:, 2] != mode]
    xyz_file_path = xyz_file_path
    print(xyz_file_path)
    np.savetxt(xyz_file_path, data, fmt='%.6f')
    grd_file_path = os.path.splitext(xyz_file_path)[0] + '.grd'
    # os.system(f'gmt xyz2grd {filtered_vel_xyz} -G{grd_file_path} -Rg -I0.1')
    os.system(f'gmt xyz2grd {xyz_file_path} -G{grd_file_path} -R{min_lon}/{max_lon}/{min_lat}/{max_lat} -I0.1')
    return grd_file_path

# Function to extract period from filename, this use '007' from 'gridvel file name, period = 1/float(0.007)... etc
def extract_period(file):
    period = re.search(r'gridvel\.\d+\.\d+\.\d+\.(\d+)', file).group(1)
    period = 1/float(period)
    return period


# Function to plot grid files using PyGMT
def plot_grd_file(grd_file):
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
    # find std files under the std_files directory
    grd_path = vel_path
    grd_file_path = os.path.join(grd_path, grd_file)
    stats = calculate_statistics(grd_file_path)
    region = [min_lon, max_lon-1, min_lat, max_lat-1]
    

    # Adjust max_val to ensure distinct color nodes
    max_val = stats['max_val'] if stats['max_val'] != stats['min_val'] else stats['max_val'] + 1e-6
    min_val = stats['min_val']
    inter = (max_val - min_val)/10
    print(mini, maxi, interi)






    fig.basemap(region=region, projection="M6i", frame=True)

     # Add title with period
    fig.text(x=region[0] + (region[1] - region[0]) / 2, y=region[3] + (region[3] - region[2]) * 0.05, text=f"Period: {period}", font="20p,Helvetica-Bold", justify="CM")



    # shading="+d",
    # with minimum and maximum values -2000 to 5000 meter
    pygmt.makecpt(cmap="gray", series=[-2000, 7000])
    fig.grdimage(grid=topo_data, region=region, projection="M6i",  frame=True, shading=True)
    
    
    cpt_file = "custom_seis.cpt"
    pygmt.makecpt(series=[mini, maxi, interi], cmap='seis', continuous=False, output=cpt_file)

    #with open(cpt_file, 'a') as cpt:
            # Set below 0.0001 and above 0.1 to light gray (240/240/240)
            # cpt.write(f"B {mini} 240/240/240 {mini} 240/240/240\n")
            # cpt.write(f"F {maxi} 240/240/240 {maxi} 240/240/240\n")
            # # Optionally, handle NaN values with a different color
            # cpt.write("N 128/128/128\n")
            
#     #cpt_file_2 = pygmt.makecpt(cmap="seis", series=[mini, maxi, inter], output=cpt_file)



    fig.grdimage(grid=grd_file_path, region=region, projection="M6i", frame=True, cmap=cpt_file, t = 60)

    #Plot and annotate phase velocity data, use fixed scale
    
    fig.colorbar(cmap=cpt_file, frame='af+l"c (km/s)"')

    # #add title, only period name, (above figure) fontsize=20, fontweight='bold'
    

    
    # # Enhanced coastlines, shorelines, and borders
    # #fig.grdimage(grid=grd_file_path, cmap=True, region=region, projection="M6i", frame=True, t=10)
    fig.coast(shorelines=True, borders=[1, 2], region=region, projection="M6i", frame=True)

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

    

    
    output_file = os.path.join(plots_path, f"{os.path.splitext(grd_file)[0]}.png")
    fig.savefig(output_file)
    print(f"Saved plot: {output_file}")

# first sort all the gridvel files
vel_files.sort()
# convert all the gridvel files to grd files
for vel_file in vel_files:
    # first remove any existing xyz files, and grd files
    
    xyz_file = os.path.join(vel_path, vel_file)
    print(xyz_file)
    # convert to period
    # get 0.007 from gridvel.
    freq = vel_file.split('.')[1]
    freq_new = '0.'+freq
    freq_new = float(freq_new)
    period = 1/freq_new
    period = round(period)
    print(period)


    # convert to grd
    grd_file = xyz2grd(xyz_file)
    #print(grd_file)

# list all the grd files
grd_list = [f for f in os.listdir(vel_path) if f.endswith('.grd')]
grd_list.sort()
for grd_file in grd_list:
    # plot the grd file
    plot_grd_file(grd_file)
    # # plot the grd file
    #plot_grd_file(grd_file)
