import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# get script path
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)

input_first_folder = 'final25'
input_folder = 'TPWT_2'

# input file name
input_file_name = 'sens143s20km.dat'

# create paths
input_file_path = os.path.join(script_path, input_first_folder, input_folder, input_file_name)

# Read the data from the input file and convert it df pandas dataframe, start reading from 3rd line
data = pd.read_csv(input_file_path, sep='   ', header=None, skiprows=2)


# Ensure data columns are numeric
data = data.apply(pd.to_numeric, errors='coerce')

# Drop rows with NaN values which might occur due to conversion issues
data = data.dropna()

print(data)

x = data[0]
print(x)
y = data[1]
print(y)
amp = data[2]
print(amp)
phase = data[3]
print(phase)

# plot x,y, amp and x,y, phase in different plots, on a two different map views

# Create figure and axis objects
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
# Define x-axis ticks
x_ticks = np.linspace(min(x), max(x), 5)

# Plot amplitude
sc1 = axes[0].scatter(x, y, c=amp, cmap='viridis', marker='o', edgecolor='none')
axes[0].set_title('Amplitude')
axes[0].set_xlabel('X (km)')
axes[0].set_ylabel('Y (km)')
axes[0].set_xticks(x_ticks)  # Set x-axis ticks
fig.colorbar(sc1, ax=axes[0], label='Amplitude')

# Plot phase
sc2 = axes[1].scatter(x, y, c=phase, cmap='coolwarm', marker='o', edgecolor='none')
axes[1].set_title('Phase')
axes[1].set_xlabel('X (km)')
axes[1].set_ylabel('Y (km)')
axes[0].set_xticks(x_ticks)  # Set x-axis ticks
fig.colorbar(sc2, ax=axes[1], label='Phase')

# Show plot
plt.tight_layout()
plt.savefig('TPWT_sens_kern_plot_2D.png')

# also plot it on 1D x vs amplitude and x vs phase
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

# Plot amplitude with line
axes[0].plot(x, amp, color='blue', marker='o', linestyle='-', label='Amplitude')
axes[0].set_title('Amplitude')

# Plot phase with line
axes[1].plot(x, phase, color='red', marker='o', linestyle='-', label='Phase')
axes[1].set_title('Phase')

# Show plot
plt.tight_layout()
plt.savefig('TPWT_sens_kern_plot_1D.png')







