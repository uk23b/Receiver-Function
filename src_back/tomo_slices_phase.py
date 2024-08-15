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

point1 = [49.0, 37.0] # [longitude, latitude]
point2 = [49.0, 43.5] # [longitude, latitude]
spacing_deg = 0.01  # Spacing between points in degrees

grid = load_earth_relief(resolution="30s", region=[36, 52, 36, 45])
topo_data = grid

fig = pygmt.Figure()

def create_line_with_elevation(point1, point2, spacing_deg, grid):
    """
    Creates a line between two points with the desired spacing in degrees and fetches elevation data.

    Parameters:
    - point1: The starting point [longitude, latitude].
    - point2: The ending point [longitude, latitude].
    - spacing_deg: The desired spacing between points in degrees.
    - grid: The loaded earth relief grid from which to fetch elevation data.

    Returns:
    - A pandas DataFrame containing the interpolated points along the line, with elevation data.
    """
    # Calculate the number of points needed, assuming spacing in degrees
    distance = np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    num_points = int(np.ceil(distance / spacing_deg)) + 1

    # Linearly interpolate the points
    x_points = np.linspace(point1[0], point2[0], num_points)
    y_points = np.linspace(point1[1], point2[1], num_points)

    # Create a DataFrame
    points_df = pd.DataFrame({
        'longitude': x_points,
        'latitude': y_points
    })

    # Fetch elevation data for each point
    elevation_data = pygmt.grdtrack(points=points_df, grid=grid, newcolname='elevation')

    return elevation_data

# Load the earth relief grid
grid = load_earth_relief(resolution="30s", region=[37, 52, 36, 45])

# Generate the line with elevation data
line_with_elevation_df = create_line_with_elevation(point1, point2, spacing_deg, grid)
print(line_with_elevation_df)


def plot_elevation_profile(line_with_elevation_df):
    """
    Plots the elevation profile from a DataFrame containing longitude, latitude, and elevation data.

    Parameters:
    - line_with_elevation_df: A pandas DataFrame with columns ['longitude', 'latitude', 'elevation'].
    """
    # Calculate the cumulative distance along the profile
    distances = np.sqrt(np.diff(line_with_elevation_df['longitude'])**2 + np.diff(line_with_elevation_df['latitude'])**2) * 111.32
    cumulative_distance = np.insert(np.cumsum(distances), 0, 0)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(cumulative_distance, line_with_elevation_df['elevation'], marker='o', linestyle='-', color='blue')
    plt.title('Elevation Profile')
    plt.xlabel('Distance Along Profile (km)', fontsize=18, fontweight='bold')
    plt.ylabel('Elevation (m)', fontsize=18, fontweight='bold')
    plt.grid(True)
    plt.savefig('elevation_profile.png')

plot_elevation_profile(line_with_elevation_df)








# script path
script = os.path.abspath(__file__)
# script directory
script_dir = os.path.dirname(script)
# change directory to the script directory
os.chdir(script_dir)


main_input_path = '/Users/utkukocum/Desktop/RF_Surf/final25/Dispersion_Grid_Files'
TPWT_folder = 'TPWT'
TPWT_folder_path = os.path.join(main_input_path, TPWT_folder)
TPWT_files = os.listdir(TPWT_folder_path)
TPWT_files.sort()
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

# create a dataframe from all_values list
df = pd.DataFrame(all_values, columns=['Period', 'Lon', 'Lat', 'Velocity'])
# write to a csv file
df.to_csv(os.path.join(main_input_path, 'TPWT_all_values.csv'), index=False)

print(df.head())



# lets first create velocity values for each node (lon, lat) with increasing period values
def generate_points(p1, p2, spacing=0.1):
    """Generate evenly spaced points between two geographic coordinates."""
    lon1, lat1 = p1
    lon2, lat2 = p2
    num_points = max(int(abs(lon2 - lon1) / spacing) + 1, int(abs(lat2 - lat1) / spacing) + 1)
    lons = np.linspace(lon1, lon2, num_points)
    lats = np.linspace(lat1, lat2, num_points)
    return np.array(list(zip(lons, lats)))

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

# Plotting
plt.figure(figsize=(14, 8))

# Define levels for the contour plot
levels = np.arange(3.3, 4.4, 0.1)  # 4.4 is used to include 4.3 as the last level

# Create the filled contour plot
cp = plt.contourf(node_idx_grid, period_grid, velocity_grid, levels=levels, cmap='viridis', extend='both')

# Add contour lines to highlight anomalies
contour_lines = plt.contour(node_idx_grid, period_grid, velocity_grid, levels=levels, colors='black', linewidths=0.5)

# Label the contours
plt.clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')

# Add a color bar with the defined levels
cbar = plt.colorbar(cp, ticks=levels, label='Velocity (km/s)')
cbar.ax.set_yticklabels(['{:.1f}'.format(vel) for vel in levels])  # set ticks as desired format

# Check if longitude is constant
if np.allclose(points[:, 0], points[0, 0], atol=1e-6):
    # Longitude is constant, use latitude for x-axis
    x_labels = points[:, 1]  # Latitude values
    x_label = 'Latitude'
    # Find indices where latitude changes by 0.5
    tick_indices = np.where(np.isclose(x_labels % 0.5, 0, atol=1e-2))[0]
else:
    # Latitude is constant, use longitude for x-axis
    x_labels = points[:, 0]  # Longitude values
    x_label = 'Longitude'
    # Find indices where longitude changes by 0.5
    tick_indices = np.where(np.isclose(x_labels % 0.5, 0, atol=1e-2))[0]

# Set x-ticks to correspond to the selected nodes
plt.xticks(ticks=tick_indices, labels=["{:.2f}".format(x_labels[idx]) for idx in tick_indices])

# Set the axis labels
plt.xlabel(x_label)
plt.ylabel('Period (s)')

# Optionally invert the y-axis if you want shallow periods at the top
plt.gca().invert_yaxis()

# Set the title
plt.title('Seismic Velocity Cross-Section with Contour Lines')

# Show the plot
plt.show()