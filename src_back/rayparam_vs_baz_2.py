import os
import obspy
import matplotlib.pyplot as plt
import numpy as np

# Define the main path and station specifics
main_path = '/Volumes/UNTITLE/18_final_products/final_25/RAWDATA/GOOD_DATA/'
station = 'YRD'
eqr_file = '.eqr'

# Get the script path
script_path = os.path.dirname(os.path.realpath(__file__))

# List only folders in the main path
folders = [f for f in os.listdir(main_path) if os.path.isdir(os.path.join(main_path, f))]

# Initialize min and max values for normalization later
min_baz, max_baz = float('inf'), float('-inf')
min_ray_param, max_ray_param = float('inf'), float('-inf')

# First, find the min and max baz and ray parameter to normalize values later
for folder in folders:
    folder_path = os.path.join(main_path, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(folder_path, file)
        st = obspy.read(file_path)[0]
        baz = st.stats.sac['baz']
        ray_param = st.stats.sac['user4']
        min_baz = min(min_baz, baz)
        max_baz = max(max_baz, baz)
        min_ray_param = min(min_ray_param, ray_param)
        max_ray_param = max(max_ray_param, ray_param)

# Create subplots for each type of data
fig, (ax_baz, ax_ray_param) = plt.subplots(2, 1, figsize=(10, 12))

# Define a scaling factor for the amplitude of the seismic data
scaling_factor_baz = 10.0  # for baz
scaling_factor_ray = 1.0   # for ray parameter

trace_color = 'blue'  # color for baz plot
trace_color_ray = 'red'  # color for ray parameter plot

# Iterate over each folder and plot for both BAZ and Ray Parameter
for folder in folders:
    folder_path = os.path.join(main_path, folder)
    files = [f for f in os.listdir(folder_path) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(folder_path, file)
        st = obspy.read(file_path)[0]
        
        # Normalize and scale data
        data_baz = st.data * scaling_factor_baz / np.max(np.abs(st.data))
        data_ray_param = st.data * scaling_factor_ray / np.max(np.abs(st.data))
        
        # Normalize baz and ray parameter values
        normalized_baz = (st.stats.sac['baz'] - min_baz) / (max_baz - min_baz) * 10  # range set to 10 for visualization
        normalized_ray_param = (st.stats.sac['user4'] - min_ray_param) / (max_ray_param - min_ray_param) * 10  # same here
        
        # Create a time axis for the seismic trace, shifting by 5 seconds for visualization purposes
        time_axis = (np.arange(0, len(data_baz)) / st.stats.sampling_rate) - 5
        
        # Plot BAZ data
        ax_baz.plot(normalized_baz, time_axis, color=trace_color, linewidth=0.05)
        
        # Plot Ray Parameter data
        ax_ray_param.plot(normalized_ray_param, time_axis, color=trace_color_ray, linewidth=0.05)

# Set labels and titles for BAZ subplot
ax_baz.set_title('Vertical Seismic Traces at Specific Back-azimuth')
ax_baz.set_xlabel('Normalized Back-azimuth')
ax_baz.set_ylabel('Time (s)')
ax_baz.invert_yaxis()
ax_baz.set_ylim(-2, 20)
ax_baz.grid(True)

# Set labels and titles for Ray Parameter subplot
ax_ray_param.set_title('Vertical Seismic Traces at Specific Ray Parameter')
ax_ray_param.set_xlabel('Normalized Ray Parameter (s/km)')
ax_ray_param.set_ylabel('Time (s)')
ax_ray_param.invert_yaxis()
ax_ray_param.set_ylim(-2, 20)
ax_ray_param.grid(True)

# Adjust layout
plt.tight_layout()

# Save the combined figure
outfile_combined = os.path.join(script_path, 'combined_traces.png')
plt.savefig(outfile_combined)


