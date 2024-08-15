import pygmt
from pylab import *
from scipy.io import netcdf_file as netcdf
from os.path import abspath, exists, join
import geopandas as gpd
import re
import numpy as np
import subprocess
from pygmt.datasets import load_earth_relief
from os.path import abspath, dirname
from os import chdir
import pandas as pd
import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import tempfile
import glob
import cartopy.crs as ccrs  # Cartopy for map projections
import os
import numpy as np
import pandas as pd
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# Define your points and grid resolution
point1 = [36.0, 40.0]  # [longitude, latitude]
point2 = [51.0, 40.0]  # [longitude, latitude]
spacing_deg = 0.01  # Spacing between points in degrees for elevation data

max_period = 100
min_period = 5

max_velocity = 4.4
min_velocity = 2.6

max_elevation = 5000
min_elevation = -500

# lets first create velocity values for each node (lon, lat) with increasing period values
def generate_points(p1, p2, spacing=0.1):
    """Generate evenly spaced points between two geographic coordinates."""
    lon1, lat1 = p1
    lon2, lat2 = p2
    num_points = max(int(abs(lon2 - lon1) / spacing) + 1, int(abs(lat2 - lat1) / spacing) + 1)
    lons = np.linspace(lon1, lon2, num_points)
    lats = np.linspace(lat1, lat2, num_points)
    return np.array(list(zip(lons, lats)))





# script path
script = os.path.abspath(__file__)
# script directory
script_dir = os.path.dirname(script)
# change directory to the script directory
os.chdir(script_dir)


main_input_path = 'main_path'
TPWT_folder = 'TPWT'
ANT_folder = 'ANT'  
TPWT_folder_path = os.path.join(main_input_path, TPWT_folder)
ANT_folder_path = os.path.join(main_input_path, ANT_folder)
TPWT_files = os.listdir(TPWT_folder_path)
TPWT_files.sort()
ANT_files = os.listdir(ANT_folder_path)
ANT_files.sort()

print(TPWT_files)

# create a list to store period values, lon, lat, and velocity values
all_values = []


# loop over TPWT files
for i in TPWT_files:
    print(i)
    # split the file name by dot
    file_name = i.split('.')
    # get the second part of the file name
    freq = (file_name[1])
    freq = '0.' + freq
    #print(freq)
    period = round(1/float(freq))  
    print(period)
    # read the TPWT file
    TPWT_file = os.path.join(TPWT_folder_path, i)
    TPWT_data = pd.read_csv(TPWT_file, sep='\s+', header=None)
    #print(TPWT_data)
    # first column is lon, second column is lat, third column is velocity
    lon = TPWT_data.iloc[:,0].values
    lat = TPWT_data.iloc[:,1].values
    vel = TPWT_data.iloc[:,2].values
    period = [period] * len(lon)
    # create tuples of lon, lat, and velocity
    values = list(zip(period, lon, lat, vel))
    # append the values to all_values list
    all_values.extend(values)
    #print(values)

# loop over ANT files
for i in ANT_files:
    print(i)
    # split the file name by dot
    file_name = i.split('.')
    # get the second part of the file name
    freq = (file_name[1])
    freq = '0.' + freq
    #print(freq)
    period = round(1/float(freq))  
    print(period)
    # read the ANT file
    ANT_file = os.path.join(ANT_folder_path, i)
    ANT_data = pd.read_csv(ANT_file, sep='\s+', header=None)
    #print(ANT_data)
    # first column is lon, second column is lat, third column is velocity
    lon = ANT_data.iloc[:,0].values
    lat = ANT_data.iloc[:,1].values
    vel = ANT_data.iloc[:,2].values
    period = [period] * len(lon)
    # create tuples of lon, lat, and velocity
    values = list(zip(period, lon, lat, vel))
    # append the values to all_values list
    all_values.extend(values)
    #print(values)

# let's add ANT data to the all_values list
# read the ANT data
    

# create a dataframe from all_values list
df = pd.DataFrame(all_values, columns=['Period', 'Lon', 'Lat', 'Velocity'])
# write to a csv file
df.to_csv(os.path.join(main_input_path, 'TPWT_ANT_all_values.csv'), index=False)

print(df.head())







# generate points between point1 and point2
points = generate_points(point1, point2)
print(points)

# Assuming df contains the full dataset with 'Period', 'Lon', 'Lat', 'Velocity'
# Filter df to contain only the points we're interested in
point_tuples = [tuple(p) for p in points]  # Convert points to a list of tuples for easy comparison
df_filtered = df[df.apply(lambda row: (row['Lon'], row['Lat']) in point_tuples, axis=1)]

# Now we need to create a 'Node_Index' column in df_filtered
# This will map each point to its corresponding index along the profile line
node_indices = {pt: idx for idx, pt in enumerate(point_tuples)}
df_filtered['Node_Index'] = df_filtered.apply(lambda row: node_indices[(row['Lon'], row['Lat'])], axis=1)


# Create a 2D grid of period and node index values
node_indices = np.arange(len(points))
period_values = np.sort(df_filtered['Period'].unique())
period_grid, node_idx_grid = np.meshgrid(period_values, node_indices, indexing='ij')

# Interpolate velocity onto the grid
velocity_grid = griddata(
    (df_filtered['Period'], df_filtered['Node_Index']), df_filtered['Velocity'],
    (period_grid, node_idx_grid), method='cubic'
)


# Fetch elevation data using PyGMT
def fetch_elevation_data(points):
    grid = pygmt.datasets.load_earth_relief(resolution="30s", region=[point1[0]-0.5, point2[0]+0.5, point1[1]-0.5, point2[1]+0.5])
    return pygmt.grdtrack(points=pd.DataFrame(points, columns=["longitude", "latitude"]), grid=grid, newcolname='elevation')

# Generate points for elevation data
points_elevation = generate_points(point1, point2, spacing_deg)
elevation_data = fetch_elevation_data(points_elevation)

# Plotting the elevation profile
fig, ax1 = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [1, 3]})

# Plot elevation profile
ax1[0].plot(points_elevation[:, 1], elevation_data['elevation'], label='Elevation')
ax1[0].set_ylabel('Elevation (m)')
ax1[0].legend()
ax1[0].set_xlabel('Distance Along Profile (km)', fontsize=18, fontweight='bold')
ax1[0].set_ylabel('Elevation (m)', fontsize=18, fontweight='bold')
# set xticks size and bold
ax1[0].tick_params(axis='x', labelsize=16, width=2)
# set yticks size and bold
ax1[0].tick_params(axis='y', labelsize=16, width=2)
ax1[0].grid(True)
ax1[0].set_title('Elevation Profile')







# Define the step for x-axis ticks as 0.5 degrees
x_tick_step = 0.5
# Calculate the indices for the x-ticks based on the tick step
tick_indices = [i for i, pt in enumerate(points) if pt[1 if point1[0] == point2[0] else 0] % x_tick_step < 0.01]
tick_labels = [f"{pt[1 if point1[0] == point2[0] else 0]:.1f}" for i, pt in enumerate(points) if i in tick_indices]

# Define velocity levels for contouring and coloring
velocity_levels = np.arange(df_filtered['Velocity'].min(), df_filtered['Velocity'].max() + 0.1, 0.1)
contour_levels = np.linspace(df_filtered['Velocity'].min(), df_filtered['Velocity'].max(), num=8)  # Less contour lines

# Plotting the velocity cross-section
cp = ax1[1].contourf(node_idx_grid, period_grid, velocity_grid, levels=velocity_levels, cmap='viridis', extend='both')
contour_lines = ax1[1].contour(node_idx_grid, period_grid, velocity_grid, levels=contour_levels, colors='black', linewidths=0.5)
ax1[1].clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')
cbar = fig.colorbar(cp, ax=ax1[1], orientation='horizontal', pad=0.1, aspect=30, ticks=np.linspace(velocity_levels.min(), velocity_levels.max(), num=len(contour_levels)))
cbar.set_label('Velocity (km/s)')


# Set x-axis ticks to every 0.5 degrees
ax1[1].set_xticks(tick_indices)
ax1[1].set_xticklabels(tick_labels)

# Set labels and invert y-axis for the cross-section plot
ax1[1].set_xlabel('Longitude' if point1[0] == point2[0] else 'Latitude')
ax1[1].set_ylabel('Period (s)')
ax1[1].set_title('Velocity Cross-Section', fontsize=18, fontweight='bold')
ax1[1].set_xlabel('Distance Along Profile (km)', fontsize=18, fontweight='bold')
ax1[1].set_ylabel('Period (s)', fontsize=18, fontweight='bold')
# set xticks size and bold
ax1[1].tick_params(axis='x', labelsize=16, width=2)
# set yticks size and bold
ax1[1].tick_params(axis='y', labelsize=16, width=2)
ax1[1].invert_yaxis()

# Show the plot
plt.tight_layout()
plt.savefig(os.path.join(main_input_path, f'cross_section_{point1[0]}_{point1[1]}_{point2[0]}_{point2[1]}.png'))
print('Path is: ', os.path.join(main_input_path, f'cross_section_{point1[0]}_{point1[1]}_{point2[0]}_{point2[1]}.png'))



