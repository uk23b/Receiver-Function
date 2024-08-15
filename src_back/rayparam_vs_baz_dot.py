import os
import obspy
import shutil
import matplotlib.pyplot as plt


# main path
main_path = '/Volumes/UNTITLE/18_final_products/final_25/RAWDATA/GOOD_DATA/'


# good folder
good_folder = 'GOOD'
# station name
station = 'YRD'
# .eqr file
eqr_file = '.eqr'

# current script path
script_path = os.path.dirname(os.path.realpath(__file__))
print(script_path)

# list only folders
folders = [f for f in os.listdir(main_path) if os.path.isdir(os.path.join(main_path, f))]
print(folders)

# folders path
folders_path = [os.path.join(main_path, f) for f in folders]

# Initialize lists to hold baz and ray parameters
baz_values = []
ray_param_values = []
#Initialize lists to hold plot data
plot_data = []


for folder in folders:
    files = [f for f in os.listdir(os.path.join(main_path, folder)) if f.endswith(eqr_file) and station in f]
    for file in files:
        file_path = os.path.join(main_path, folder, file)
        st = obspy.read(file_path)
        
        # Assuming you have a way to determine baz and ray_param for each station file
        baz = st[0].stats.sac['baz']
        ray_param = st[0].stats.sac['user4']
        
        # Normalize time series for plotting
        data = st[0].data / max(abs(st[0].data))
        
        # Append the data along with its baz and ray_param for plotting
        plot_data.append((baz, ray_param, data))

# Determine min and max for ray_param to scale plots vertically
ray_params = [d[1] for d in plot_data]
min_ray_param, max_ray_param = min(ray_params), max(ray_params)

fig, ax = plt.subplots(figsize=(10, 6))

for baz, ray_param, data in plot_data:
    # Scale and offset time series vertically based on ray_param
    offset = (ray_param - min_ray_param) / (max_ray_param - min_ray_param) * 10  # Adjust scale factor as needed
    times = range(len(data))  # Simplified x-axis; consider scaling according to actual time
    ax.plot([baz] * len(data), data + offset, linewidth=0.5)  # Plot each time series at its baz, offset by its ray_param

ax.set_xlabel('Back-azimuth (degrees)')
ax.set_ylabel('Ray Parameter (scaled and offset)')
plt.title('Time Series by Back-azimuth and Ray Parameter')
plt.grid(True)
outfile = os.path.join(script_path, 'rayparam_vs_baz.png')
plt.savefig(outfile)
        

        


    
    