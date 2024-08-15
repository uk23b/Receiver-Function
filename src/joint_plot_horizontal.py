import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os, sys, re
import pygmt
import csv



max_depth = 200  # Maximum depth to extract velocity data
fitting_threshold = 0.0  # Fitting value threshold
std_dev_threshold = 2.5  # Standard deviation threshold
min_lat, max_lat = 38.0, 43.3  # Fixed plotting region latitudes
min_lon, max_lon = 41.0, 51.0  # Fixed plotting region longitudes
# Option to use absolute value or normal value for fitting
use_absolute_value_for_fitting = True  # Set to False if you want to use the normal values
S_min = 2.5  # Minimum S velocity for the color scale
S_max = 5.0  # Maximum S velocity for the color scale

    # # Define the fixed geographical boundaries
    # min_lon = 41
    # max_lon = 51
    # min_lat = 38.0
    # max_lat = 43.3
    # region = [min_lon, max_lon, min_lat, max_lat]
    # S_min = 2.5
    # S_max = 5.0
    # interi = (S_max - S_min)/10



# Placeholder for topographical data (ensure this is correctly set up)
topo_data = '@earth_relief_30s' 

output_folder = '/Users/utkukocum/Desktop/RF_Surf/final25/data/JOINT/work_joint_test_1/plot_outputs/'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Output file folder
output_folder = '/Users/utkukocum/Desktop/RF_Surf/final25/data/JOINT/work_joint_test_1/plot_outputs/'

# If output folder does not exist, create it
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def extract_last_fitting_value(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        return None  # Return None if file does not exist

    with open(file_path, 'r', encoding='latin-1') as file:
        content = file.read()

    # Use a regular expression to find all occurrences of the fitting value
    fitting_values = re.findall(r'Percent of Signal Power Fit \(RFTN\)\s+:\s+([-\d.]+)%', content)
    # Extract the last fitting value if it exists
    return fitting_values[-1] if fitting_values else None

def extract_lon_lat_from_filename(filename):
    # Regular expression to extract longitude and latitude from filename
    match = re.search(r'(\d+\.\d+)_(\d+\.\d+)\.txt$', filename)
    if match:
        lon, lat = match.groups()
        return float(lon), float(lat)
    else:
        return None, None  # or handle error

def parse_velocity_file(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        return []  # Return an empty list if file does not exist

    with open(file_path, 'r', encoding='latin-1') as file:
        lines = file.readlines()

    # Find the start of the velocity data
    start_index = None
    for i, line in enumerate(lines):
        if "DEPTH THICKNESS     S-VEL" in line:
            start_index = i + 1
            break

    if start_index is None:
        return []  # or handle error

    # Extract velocity data
    velocity_data = []
    for line in lines[start_index:]:
        if line.strip() == "":
            break  # End of velocity data
        parts = re.split(r'\s+', line.strip())
        # Check if the line contains numeric values for depth and velocity
        try:
            depth, velocity = float(parts[0]), float(parts[2])
            velocity_data.append((depth, velocity))
        except ValueError:
            # Skip lines that do not contain numeric values for depth and velocity
            continue

    return velocity_data

# Source file folder
source_folder_main = '/Users/utkukocum/Desktop/RF_Surf/final25/data/JOINT/work_joint_test_1/input_folders/'

# List the folders in the source folder
source_folders = os.listdir(source_folder_main)
# Filter only folders
source_folders = [i for i in source_folders if os.path.isdir(os.path.join(source_folder_main, i))]
# Sort folders
source_folders = sorted(source_folders)

# Create an empty list to store the final tuple structure
lon_lat_velocity_fitting_source_depth_folder = []

for source_folder in source_folders:
    source_folder_path = os.path.join(source_folder_main, source_folder)
    source_files = os.listdir(source_folder_path)
    source_files = [i for i in source_files if i.endswith('.txt')]
    source_files_path = [os.path.join(source_folder_path, i) for i in source_files]
    
    # From file names, extract lon and lat, parse the velocity data, and get the fitting value
    for file_path in source_files_path:
        lon, lat = extract_lon_lat_from_filename(file_path)
        velocity_data = parse_velocity_file(file_path)
        fitting_value = extract_last_fitting_value(file_path)  # Get the fitting value
        # Append data to the list, including the fitting value
        lon_lat_velocity_fitting_source_depth_folder.append((lon, lat, velocity_data, fitting_value, file_path, source_folder))

# Write to CSV file
output_csv_file = os.path.join(output_folder, 'velocity_data.csv')
with open(output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    # Write the headers, including a header for fitting values
    csvwriter.writerow(['Longitude', 'Latitude', 'Depth', 'Velocity', 'Fitting Value', 'Source File', 'Source Folder'])

    # Write the data
    for data in lon_lat_velocity_fitting_source_depth_folder:
        lon, lat, velocity_data, fitting_value, source_file, source_folder = data
        # Write each depth and velocity pair on a separate row, including the fitting value
        for depth_velocity_pair in velocity_data:
            depth, velocity = depth_velocity_pair
            # Include the fitting value in the row
            csvwriter.writerow([lon, lat, depth, velocity, fitting_value, source_file, source_folder])

# Read the CSV file
df = pd.read_csv(output_csv_file)

# Filter the data by depth
df = df[df['Depth'] <= max_depth]

# Convert the 'Fitting Value' column to numeric, because it may contain non-numeric values
df['Fitting Value'] = pd.to_numeric(df['Fitting Value'], errors='coerce')

# Apply the absolute value if the option is set
if use_absolute_value_for_fitting:
    df['Fitting Value'] = df['Fitting Value'].abs()

# Filter out rows where the 'Fitting Value' is below the threshold
df_filtered = df[df['Fitting Value'] >= fitting_threshold]

# Group by 'Depth', 'Longitude', and 'Latitude' and get the index of the row with the highest 'Fitting Value'
idx = df_filtered.groupby(['Depth', 'Longitude', 'Latitude'])['Fitting Value'].idxmax()

# Use the indices to filter the DataFrame
df_best_fit = df_filtered.loc[idx]

# Sort the DataFrame for better readability if needed
df_best_fit = df_best_fit.sort_values(by=['Depth', 'Longitude', 'Latitude'])

unique_depths = sorted(set(df_best_fit['Depth']))

# Create output folder if not exist (named as f'{fitting_threshold}_output_plots') for thresholded data
output_folder_threshold = os.path.join(output_folder, f'{fitting_threshold}_output_plots')
if not os.path.exists(output_folder_threshold):
    os.makedirs(output_folder_threshold)



# Filter the data by depth and fitting value threshold
df = pd.read_csv(output_csv_file)
df = df[df['Depth'] <= max_depth]
df['Fitting Value'] = pd.to_numeric(df['Fitting Value'], errors='coerce')
if use_absolute_value_for_fitting:
    df['Fitting Value'] = df['Fitting Value'].abs()
df_filtered = df[df['Fitting Value'] >= fitting_threshold]

# Group by 'Depth', 'Longitude', and 'Latitude' and get the index of the row with the highest 'Fitting Value'
idx = df_filtered.groupby(['Depth', 'Longitude', 'Latitude'])['Fitting Value'].idxmax()
df_best_fit = df_filtered.loc[idx]

unique_depths = sorted(set(df_best_fit['Depth']))

# Create output folder for thresholded data
output_folder_threshold = os.path.join(output_folder, f'{fitting_threshold}_output_plots')
if not os.path.exists(output_folder_threshold):
    os.makedirs(output_folder_threshold)

for target_depth in unique_depths:
    
    # Filter data for the current depth
    depth_data = df_best_fit[df_best_fit['Depth'] == target_depth]

    # Calculate mean and standard deviation for the current depth
    mean_velocity = depth_data['Velocity'].mean()
    std_velocity = depth_data['Velocity'].std()

    # # Filter out the outliers for the current depth
    # depth_data = depth_data[
    #     (depth_data['Velocity'] >= (mean_velocity - std_dev_threshold * std_velocity)) &
    #     (depth_data['Velocity'] <= (mean_velocity + std_dev_threshold * std_velocity))
    # ]

    # Get the range for S velocity for the current depth
    #S_min = depth_data['Velocity'].min()
    #S_max = depth_data['Velocity'].max()

    # Ensure there's data left after filtering, otherwise skip to the next depth
    if depth_data.empty:
        continue

    # Generating the grid file name
    output_S_grd = f'{target_depth}km.grd'
    output_S_grd = os.path.join(output_folder_threshold, output_S_grd)

    # Write lon, lat, and S velocity to a file
    output_S = f'{target_depth}km.txt'
    output_S = os.path.join(output_folder_threshold, output_S)

    filtered_info = depth_data[['Longitude', 'Latitude', 'Velocity']]

    with open(output_S, 'w') as f:
        for row in filtered_info.itertuples():
            lon, lat, S = row.Longitude, row.Latitude, row.Velocity
            f.write(f'{lon} {lat} {S}\n')

    # Convert XYZ data to a grid
    command = f'gmt xyz2grd {output_S} -R{min_lon}/{max_lon}/{min_lat}/{max_lat} -I0.1d -G{output_S_grd}'
    os.system(command)

    # Plotting
    #interval = 0.001
    interval = (S_max - S_min) / 10
    fig = pygmt.Figure()
    title_str = f'+t" Depth = {target_depth} km "'
    fig.basemap(region=[min_lon, max_lon, min_lat, max_lat], projection="M8i", frame=["a", title_str])
    # Ensure topo_data is properly loaded
    # fig.grdimage(grid=topo_data, cmap='gray')
    pygmt.makecpt(series=[S_min, S_max, interval], cmap="seis", continuous=True)
    #fig.coast(shorelines=True, borders='1/0.5p', water='lightblue')
    fig.coast(shorelines=True, borders='1/0.5p')
    fig.grdimage(grid=output_S_grd, transparency=60)
    color_bar_length = max_lat - min_lat
    fig.colorbar(frame='+l"S velocity (km/s)"', position=f"JMR+o1c/0c+w{color_bar_length}c/0.5c", box=True)
    #fig.colorbar(frame='+l" "', position="x21.5c/14.0c+w14c+jTC+v")
    
    # fig.show()

    # Save figure
    output_fig = f'{target_depth}km.png'
    output_fig = os.path.join(output_folder_threshold, output_fig)
    # save location

    print(output_fig)

    fig.savefig(output_fig)