import os
import obspy
import shutil
import matplotlib.pyplot as plt
import numpy as np

# Get the script path
script_path = os.path.dirname(os.path.realpath(__file__))

# Define the main path and station specifics
main_path = '/Volumes/UNTITLE/18_final_products/final_25/RAWDATA/GOOD_DATA/'
station = 'YRD'
eqr_file = '.eqr'

# List only folders in the main path
folders = [f for f in os.listdir(main_path) if os.path.isdir(os.path.join(main_path, f))]

# Initialize min and max baz for normalization later
min_baz, max_baz = float('inf'), float('-inf')

# First, find the min and max baz to normalize baz values later
for folder in folders:
    folder_path = os.path.join(main_path, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(folder_path, file)
        st = obspy.read(file_path)[0]
        baz = st.stats.sac['baz']
        min_baz = min(min_baz, baz)
        max_baz = max(max_baz, baz)

# Create the figure for plotting
fig, ax = plt.subplots(figsize=(10, 6))

# Define a scaling factor for the amplitude of the seismic data
scaling_factor = 10.0  # Adjust this as needed to scale the amplitude fluctuations

# Define a horizontal offset factor to avoid overlaying traces
horizontal_offset = 0.1  # Adjust this as needed

trace_color = 'blue'

# Iterate over each folder
for folder in folders:
    folder_path = os.path.join(main_path, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(folder_path, file)
        st = obspy.read(file_path)[0]
        baz = st.stats.sac['baz']
        
        # Scale the data
        data = st.data * scaling_factor / np.max(np.abs(st.data))
        
        # Normalize baz to have it between 0 and 1 for consistent offsetting
        normalized_baz = (baz - min_baz) / (max_baz - min_baz)
        horizontal_position = normalized_baz * horizontal_offset
        
        # Create a time axis for the seismic trace
        time_axis = np.arange(0, len(data)) / st.stats.sampling_rate

        time_axis -= 5

        # Plot the time series with horizontal offset
        ax.plot(baz + data, time_axis, color=trace_color,linewidth=0.1)  # Increase linewidth for visibility

# Set the axis labels and plot title
ax.set_xlabel('Back-azimuth (degrees)',fontsize=18, fontweight='bold')
ax.set_ylabel('Time (s)',fontsize=18, fontweight='bold')
ax.tick_params(axis='both', which='major', labelsize=16, width=1.5)
plt.title(f'Receiver Functions vs Backazimuth for Station {station} ',fontsize=18)

# Invert the y-axis to have the start of the time series at the bottom and set the y-axis limits to focus on 0-20 seconds
ax.invert_yaxis()
ax.set_ylim(-2, 20)

# Show the grid
ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='grey')

outfile = os.path.join(script_path, 'baz_time.png')
plt.savefig(outfile)









# Initialize min and max ray parameter for normalization later
min_ray_param, max_ray_param = float('inf'), float('-inf')

# First, find the min and max ray parameter to normalize ray parameter values later
for folder in folders:
    folder_path = os.path.join(main_path, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(folder_path, file)
        st = obspy.read(file_path)[0]
        ray_param = st.stats.sac['user4']
        min_ray_param = min(min_ray_param, ray_param)
        max_ray_param = max(max_ray_param, ray_param)

# Create a new figure for the ray parameter plot
fig2, ax2 = plt.subplots(figsize=(10, 6))

# Define a scaling factor for the amplitude of the seismic data
scaling_factor = 1.0  # You may need to adjust this based on your dataset

# Calculate a wider spread based on the range of the ray parameters
ray_param_range = max_ray_param - min_ray_param
spread_factor = 10.0 / ray_param_range  # Adjust the 10.0 to change the spread

# Define a smaller linewidth
line_width = 0.05

# Iterate over each folder and plot
for folder in folders:
    folder_path = os.path.join(main_path, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(folder_path, file)
        st = obspy.read(file_path)[0]
        ray_param = st.stats.sac['user4']
        
        # Normalize ray parameter to spread out the traces on the plot
        normalized_ray_param = (ray_param - min_ray_param) * spread_factor
        
        # Scale the data
        data = st.data / np.max(np.abs(st.data))  # Just normalize without scaling
        
        # Create a time axis for the seismic trace
        time_axis = (np.arange(0, len(data)) / st.stats.sampling_rate) 

        # shitft y axis by 5 seconds
        time_axis -= 5

        # Plot the time series with the new normalization and linewidth
        ax2.plot(normalized_ray_param + data, time_axis, color='red', linewidth=line_width)

# Set the axis labels and plot title for the ray parameter plot
ax2.set_xlabel('Ray Parameter (s/km)',fontsize=18, fontweight='bold')
ax2.set_ylabel('Time (s)',fontsize=18, fontweight='bold')
ax2.set_title(f'Receiver Functions vs Ray Parameter for Station {station}',fontsize=18)
ax2.tick_params(axis='both', which='major', labelsize=16, width=1.5)
ax2.invert_yaxis()
ax2.set_ylim(-2, 20)
ax2.grid(True, which='both', linestyle='--', linewidth=0.5, color='grey')

# Save the ray parameter plot
outfile_rayparam = os.path.join(script_path, 'rayparam_vs_time.png')
plt.savefig(outfile_rayparam)


