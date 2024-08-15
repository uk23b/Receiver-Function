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

point1 = [45.5, 39.5] # [longitude, latitude]
point2 = [46.1, 43.0] # [longitude, latitude]
spacing_deg = 0.005
seismic_scale = 5

# Create a DataFrame with your points
points_df = pd.DataFrame({
    'longitude': [point1[0], point2[0]],
    'latitude': [point1[1], point2[1]]
})

# get script current directory
script_dir = abspath(dirname(__file__))
# change directory to the script directory
chdir(script_dir)



#topo_data = '@earth_relief_30s'  # 30 arc second global relief (SRTM15+V2.1 @ 1.0 km)



# #filename='grid2dv_smothing_100.grd'


minlon=36
maxlon=52
minlat=36.0
#minlat=35.5
maxlat=46.0

grid = load_earth_relief(resolution="30s", region=[37, 52, 36, 45])
print(grid)
topo_data = grid

fig = pygmt.Figure()
pygmt.makecpt(series=[-2000,3000,100],cmap="globe")
# fig.grdimage(grid=topo_data,region=[minlon, maxlon, minlat, maxlat],
#              projection='M6i',t=60)
# #fig.colorbar(frame=True)

# fig.colorbar(
#              frame='+l"Topography(m)"',position="x7.5c/-1.0c+w14c+jTC+h"
#              )

# fig.coast(
#           region=[minlon, maxlon, minlat, maxlat],
#           projection='M6i',
#           shorelines=True,
#           frame=True
#           )

# fig.savefig('topo.png')



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


# now load ccp receiver function data

ccp_receiver_function_path = 'your_path'
ccp_receiver_function_files = os.listdir(ccp_receiver_function_path)
# SynRF_37.200_39.800 . this is the filename format. first is lon, second is lat

# loop over line_with_elevation_df data 
print(line_with_elevation_df)

# create longitude and latitude pairs
lon_lat_pairs = []
for i in range(len(line_with_elevation_df)):
    lon = line_with_elevation_df.iloc[i,0]
    lat = line_with_elevation_df.iloc[i,1]
    lon_lat_pairs.append([lon, lat])

def find_closest_ccp_files(lon_lat_pairs, ccp_receiver_function_path):
    """
    Find the closest CCP receiver function files within 1 degree for each longitude and latitude pair.

    Parameters:
    - lon_lat_pairs: A list of [longitude, latitude] pairs.
    - ccp_receiver_function_path: Path to the directory containing CCP receiver function files.

    Returns:
    - A list of paths to the closest CCP receiver function files for each lon-lat pair.
    """
    ccp_files = os.listdir(ccp_receiver_function_path)
    closest_files = []

    for lon, lat in lon_lat_pairs:
        closest_distance = float('inf')  # Initialize with a large number
        closest_file = None
        for file in ccp_files:
            # Extract longitude and latitude from the filename
            try:
                _, file_lon, file_lat = file.split('_')
                file_lon, file_lat = float(file_lon), float(file_lat[:-4])  # Remove file extension and convert to float
                # Calculate distance and check if it's closer than the current closest
                distance = np.sqrt((lon - file_lon) ** 2 + (lat - file_lat) ** 2)
                if distance < closest_distance and distance <= 0.4999:  # Within 1 degree  ################
                    closest_distance = distance
                    closest_file = file
            except ValueError:
                # Skip files that don't match the expected filename format
                continue
        
        if closest_file:
            closest_files.append(os.path.join(ccp_receiver_function_path, closest_file))
        else:
            closest_files.append(None)  # No file found within 1 degree

    return closest_files

# Assuming you have your line_with_elevation_df and ccp_receiver_function_path set up
lon_lat_pairs = line_with_elevation_df[['longitude', 'latitude']].values.tolist()

closest_ccp_files = find_closest_ccp_files(lon_lat_pairs, ccp_receiver_function_path)

# Print the paths to the closest CCP files for each point (or None if no file is found within 1 degree)
for path in closest_ccp_files:
    if path is not None and '.txt' in path:
        # read the txt file
        df = pd.read_csv(path, engine='python', encoding='cp1252', header=None)
    # if '.txt' in path:
    #     # read the txt file
    #     df = pd.read_csv(path, engine = 'python', encoding = 'cp1252', header = None)
        #print(df)

def plot_elevation_and_seismic_traces(elevation_df, ccp_paths, seismic_scale=1):
    # Prepare the figure and main subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [1, 3]})
    
    # Calculate cumulative distance for x-axis
    distances = np.sqrt(np.diff(elevation_df['longitude'])**2 + np.diff(elevation_df['latitude'])**2) * 111.32
    cumulative_distance = np.insert(np.cumsum(distances), 0, 0)

    # Plot elevation profile on the top subplot
    # set title
    
    ax1.plot(cumulative_distance, elevation_df['elevation'], '-k')
    ax1.set_ylabel('Elevation (m)', fontsize=18, fontweight='bold')
    ax1.tick_params(axis='both', which='major', labelsize=16, width=1.5)
    ax1.set_ylim(-200, 4000)  # Set fixed y-axis limits
    ax1.grid(True)
    
    # Secondary axis for longitude and latitude
    ax1b = ax1.twiny()  # Create a twin of Axes for sharing the x-axis
    ax1b.set_xlim(ax1.get_xlim())  # Ensure the new axis has the same x-limits as the original
    ax1b.xaxis.tick_top()  # Set the ticks on the top
    ax1b.xaxis.set_label_position('top')  # Set the x-axis label on top

    tick_positions = cumulative_distance
    # Corresponding longitudes and latitudes for the ticks (can be interpolated or selected from points)
    tick_longitudes = np.interp(tick_positions, cumulative_distance, elevation_df['longitude'])
    tick_latitudes = np.interp(tick_positions, cumulative_distance, elevation_df['latitude'])

    # Format tick labels with directional suffixes
    formatted_tick_labels = ['{:.2f}°{}\n{:.2f}°{}'.format(
        abs(lon), 'E' if lon >= 0 else 'W', 
        abs(lat), 'N' if lat >= 0 else 'S'
    ) for lon, lat in zip(tick_longitudes, tick_latitudes)]

    ax1.set_title(f'Elevation Profile and CCP RF Traces from {elevation_df.iloc[0,0]:.2f}°E, {elevation_df.iloc[0,1]:.2f}°N to {elevation_df.iloc[-1,0]:.2f}°E, {elevation_df.iloc[-1,1]:.2f}°N', fontsize=20, fontweight='bold')

    # Set the tick positions and labels
    tick_spacing = len(cumulative_distance) // 5  # number of ticks to show
    ax1b.set_xticks(tick_positions[::tick_spacing])
    ax1b.set_xticklabels(formatted_tick_labels[::tick_spacing], rotation=45, ha='left',fontsize=12, fontweight='bold')

    # Plot elevation profile on the top subplot
    ax1.plot(cumulative_distance, elevation_df['elevation'], '-k')
    ax1.set_ylabel('Elevation (m)',fontsize=18, fontweight='bold')
    ax1.grid(True)
    
    # Plot seismic traces on the bottom subplot
    for i, path in enumerate(ccp_paths):
        if path and '.txt' in path:  # Ensure valid path and it's a text file
            # Load CCP data
            ccp_df = pd.read_csv(path, engine='python', encoding='cp1252', header=None, sep='\s+')
            depths = ccp_df[3]  # Assuming 4th column is depth
            amplitudes = ccp_df[4]  # Assuming 5th column is amplitude

            # Adjust amplitude scale and plot
            positive_amplitudes = amplitudes.clip(lower=0) * seismic_scale
            negative_amplitudes = amplitudes.clip(upper=0) * seismic_scale

            # Plot positive amplitudes in red and negative in blue
            ax2.fill_betweenx(depths, cumulative_distance[i], cumulative_distance[i] + positive_amplitudes, color='red', linewidth=0)
            ax2.fill_betweenx(depths, cumulative_distance[i], cumulative_distance[i] + negative_amplitudes, color='blue', linewidth=0)

    ax2.set_ylabel('Depth (km)', fontsize=18, fontweight='bold')
    ax2.set_xlabel('Distance Along Profile (km)',fontsize=18, fontweight='bold')
    # tick params
    ax2.tick_params(axis='both', which='major', labelsize=16, width=1.5)
    ax2.invert_yaxis()  # Depths should increase downwards
    ax2.grid(True)

    #
    # Define the inset position and size relative to the main figure,  for longitude changes, latitude constant)
    if point1[0] == point2[0]:
        ax_inset_position_1 = [0.665, 0.11, 0.4, 0.4]
    elif point1[1] == point2[1]:
        # rotate the inset, to fit the lower right corner
        ax_inset_position_1 = [0.50, -0.04, 0.4, 0.4]
    else:
        if abs(point1[0] - point2[0]) > abs(point1[1] - point2[1]):
            # More horizontal
            ax_inset_position_1 = [0.50, -0.04, 0.4, 0.4]  # Bottom of the figure
        else:
            # More vertical
            ax_inset_position_1 = [0.665, 0.11, 0.4, 0.4]  # Right side of the figure

    ax_inset = fig.add_axes(ax_inset_position_1)
    ax_inset.axis('off')  # Hide the axis


#     # Define the inset position and size relative to the main figure
#     ax_inset_position_1 = [0.665, 0.11, 0.4, 0.4]  # [left, bottom, width, height] (for longitude changes, latitude constant)

#     ax_inset = fig.add_axes(ax_inset_position_1)
#     ax_inset.axis('off')  # Hide the axis
    
    # Create the inset figure using PyGMT
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpfile = os.path.join(tmpdirname, 'pygmt_plot.png')
        fig_inset = pygmt.Figure()
        
        # Define the region of the map
        region = [
            elevation_df['longitude'].min() - 1, elevation_df['longitude'].max() + 1,
            elevation_df['latitude'].min() - 1, elevation_df['latitude'].max() + 1
        ]
        
        # Plot the topography on the inset map, no frame
        fig_inset.basemap(region=region, projection='M4i', frame='a')
        fig_inset.grdimage(grid=grid, cmap='geo', shading=True)
        fig_inset.plot(x=elevation_df['longitude'], y=elevation_df['latitude'], pen='2p,red')
        
        # Save the PyGMT figure to a temporary file
        fig_inset.savefig(tmpfile)
        img = plt.imread(tmpfile)
        ax_inset.imshow(img)

    #plt.tight_layout()
    # save the plot with input coordinates
    plt.savefig(f'elevation_and_seismic_traces_{elevation_df.iloc[0,0]}_{elevation_df.iloc[0,1]}_{elevation_df.iloc[-1,0]}_{elevation_df.iloc[-1,1]}.png')


plot_elevation_and_seismic_traces(line_with_elevation_df, closest_ccp_files, seismic_scale=seismic_scale)

# For each CCP file, let's try to find moho depth by using depth axis and amplitude axis
# We can use the maximum amplitude point (positive side) as the moho depth, however there are multiple peaks in the amplitude axis
# moho depth is generally between 20-60 km, so we can use this information to filter out the peaks...

def find_moho_depth(ccp_df, min_depth=15, max_depth=60):
    """
    Finds the Moho depth by looking for the maximum positive amplitude within a depth range.

    Parameters:
    ccp_df (DataFrame): DataFrame containing depth and amplitude information from CCP data.
    min_depth (float): Minimum depth to consider for Moho (in km).
    max_depth (float): Maximum depth to consider for Moho (in km).

    Returns:
    float: The estimated Moho depth in kilometers, or None if no significant peak is found.
    """
    # Filter data within the Moho depth range
    moho_region_df = ccp_df[(ccp_df[3] >= min_depth) & (ccp_df[3] <= max_depth)]
    
    if not moho_region_df.empty:
        # Find the index of the maximum amplitude in the Moho region
        max_amp_index = moho_region_df[4].idxmax()
        moho_depth = moho_region_df.loc[max_amp_index, 3]
        return moho_depth
    else:
        return None
    

def get_all_ccp_paths(ccp_receiver_function_path):
    """
    Gets all CCP receiver function file paths with .txt extension within the given directory.

    Parameters:
    ccp_receiver_function_path (str): Path to the directory containing CCP receiver function files.

    Returns:
    List[str]: A list of paths to the CCP receiver function files.
    """
    # Use glob to get all .txt files in the directory
    ccp_files = glob.glob(os.path.join(ccp_receiver_function_path, '*.txt'))
    return ccp_files

def extract_lon_lat_from_filename(filename):
    """
    Extracts longitude and latitude from a CCP filename with the expected format 'SynRF_lon_lat'.

    Parameters:
    filename (str): The filename to extract coordinates from.

    Returns:
    tuple: (longitude, latitude) as floats.
    """
    # Extract the part of the filename without extension
    base_name = os.path.basename(filename)
    base_name = os.path.splitext(base_name)[0]

    # Assuming the filename format is 'SynRF_lon_lat'
    parts = base_name.split('_')
    if len(parts) == 3 and parts[0] == 'SynRF':
        lon, lat = map(float, parts[1:])
        return lon, lat
    else:
        raise ValueError(f"Filename does not match expected format: {filename}")

def create_lon_lat_moho_pairs(ccp_receiver_function_path):
    """
    Creates a list of tuples with longitude, latitude, and estimated Moho depth.

    Parameters:
    ccp_receiver_function_path (str): The directory containing CCP receiver function files.

    Returns:
    List[tuple]: A list of (longitude, latitude, Moho depth) tuples.
    """
    all_ccp_files = glob.glob(os.path.join(ccp_receiver_function_path, 'SynRF_*.txt'))
    lon_lat_moho_pairs = []

    for file_path in all_ccp_files:
        # Extract longitude and latitude from the file name
        try:
            lon, lat = extract_lon_lat_from_filename(file_path)
        except ValueError as e:
            print(e)
            continue  # Skip files that do not match the expected format

        # Load the CCP data from the file
        ccp_df = pd.read_csv(file_path, engine='python', encoding='cp1252', header=None, sep='\s+')
        
        # Find the Moho depth
        moho_depth = find_moho_depth(ccp_df)
        if moho_depth is not None:
            lon_lat_moho_pairs.append((lon, lat, moho_depth))

    return lon_lat_moho_pairs


ccp_receiver_function_path = '/Users/utkukocum/Desktop/RF_Surf/final25_good/CCPDATA_dilate/RFs_proc_25_hit10'
ccp_files = get_all_ccp_paths(ccp_receiver_function_path)
lon_lat_moho_depths = create_lon_lat_moho_pairs(ccp_receiver_function_path)

# Display the list of (longitude, latitude, Moho depth) tuples
for item in lon_lat_moho_depths:
    print(item)

def plot_moho_depth_map_pygmt(lon_lat_moho_depths, minlon=41):
    """
    Plots the Moho depth for given locations on a map using PyGMT, filtering for longitudes greater than minlon.
    
    Parameters:
    - lon_lat_moho_depths (list of tuples): Each tuple contains (longitude, latitude, moho_depth).
    - minlon (float): Minimum longitude to consider for plotting.
    """
    # Filter for longitudes greater than minlon
    filtered_data = [pt for pt in lon_lat_moho_depths if pt[0] > minlon]
    
    # Unpack the filtered data
    lons, lats, moho_depths = zip(*filtered_data) if filtered_data else ([], [], [])
    
    # Create a PyGMT figure
    fig = pygmt.Figure()
    
    # Check if we have any data to plot
    if not filtered_data:
        print("No data to plot after filtering for longitude greater than", minlon)
        return
    
    # Define the region of interest, ensuring longitude starts at minlon
    region = [
        max(minlon, min(lons)) - 1, max(lons) + 1,
        min(lats) - 1, max(lats) + 1
    ]
    
    # Create the color palette table for Moho depths
    pygmt.makecpt(cmap="seis", series=[min(moho_depths), max(moho_depths)])

    # Plot the base map with coastlines
    fig.basemap(region=region, projection="M15c", frame=["af", "WSne+t\"Moho Depth Distribution\""])
    fig.coast(shorelines=True, water="lightblue")
    
    # Plot the Moho depth points, size is defined within `style` (e.g., 'c0.2c' for circles of 0.2 cm)
    fig.plot(x=lons, y=lats, style="c0.2c", color=moho_depths, cmap=True, pen="black")

    # Add a color bar to indicate the Moho depth values
    fig.colorbar(frame=["x+l\"Moho Depth (km)\"", "y+lm"])

    # Save the figure
    fig.savefig("moho_depth_map.png")

    

# plot_moho_depth_map_pygmt(lon_lat_moho_depths, minlon=41)

# # Assuming lon_lat_moho_depths is populated with your data
# data = np.array(lon_lat_moho_depths)

# # Define a function to check for close neighbors
# def has_close_neighbor(point, data, threshold=0.1):
#     distances = np.sqrt((data[:, 0] - point[0])**2 + (data[:, 1] - point[1])**2)
#     return np.any((distances > 0) & (distances < threshold))

# # Filter the data for longitudes greater than 40 and check for close neighbors
# filtered_data = np.array([pt for pt in data if pt[0] > 40 and has_close_neighbor(pt, data)])

# region = [40, np.max(filtered_data[:, 0])+0.5, np.min(filtered_data[:, 1])-0.5, np.max(filtered_data[:, 1])+0.5]
# spacing = "0.1"  # Ensure spacing is a string for PyGMT compatibility


# # Create the grid
# grid = pygmt.surface(x=filtered_data[:, 0], y=filtered_data[:, 1], z=filtered_data[:, 2], region=region, spacing=spacing)

# # Plot the gridded data
# fig = pygmt.Figure()

# # Basemap with grid and coastlines
# fig.basemap(region=region, projection="M6i", frame=True)
# fig.grdimage(grid=grid, cmap="seis")

# # make it between 15 and 60 km


# # Add colorbar
# fig.colorbar(frame=['x+l"Depth (km)"'])

# # Plot coastlines for context
# fig.coast(shorelines=True)

# # Save the figure
# fig.savefig('moho_depth_map_filtered.png')




