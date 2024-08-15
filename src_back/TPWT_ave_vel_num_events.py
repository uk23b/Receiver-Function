import os
import matplotlib.pyplot as plt

# get script path
script_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(script_path)


# Define the periods, number of events, and corresponding velocities
periods = [25, 29, 33, 40, 50, 66, 80, 100, 111, 125, 143]
num_events = [71, 78, 83, 86, 80, 82, 82, 79, 85, 86, 88]
vel_corespnd = [3.3891, 3.4544, 3.58790, 3.6569, 3.7341, 3.8191, 3.8770, 3.9702, 4.0289, 4.1112, 4.1856]

# Create a figure that contains number of events vs period with bar plot and also put line plot of average velocity vs period
fig, ax1 = plt.subplots(figsize=(10, 8))
ax2 = ax1.twinx()

# Calculating the width for bars to appear more continuous
period_width = [p2 - p1 for p1, p2 in zip(periods[:-1], periods[1:])]  # Calculate differences between consecutive periods
period_width.append(period_width[-1])  # Duplicate the last width for the final bar
bar_width = [w * 0.8 for w in period_width]  # Make the bars cover 80% of the interval to the next period

# Plotting
bars = ax1.bar(periods, num_events, color='blue', alpha=0.7, label='Number of Events', width=bar_width)
line = ax2.plot(periods, vel_corespnd, color='red', linestyle='-', marker='o', label='Average Velocity')

# Setting x-axis specifically for period values
ax1.set_xticks(periods)  # Set x-ticks to be exactly at the period values
ax1.set_xticklabels(periods)  # Set x-tick labels to show period values

# set the fonsize for ticks
ax1.tick_params(axis='both', which='major', labelsize=14, width=1.0)
ax2.tick_params(axis='both', which='major', labelsize=14, width=1.0)


# Adjusting y-axis limits for the number of events
ax1.set_ylim(70, 95)  # Set y-limits for number of events

# Labeling
ax1.set_xlabel('Period (s)', fontsize=14, fontweight='bold')
ax1.set_ylabel('Number of Events', color='blue', fontsize=14, fontweight='bold')
ax2.set_ylabel('Average Velocity (km/s)', color='red', fontsize=14, fontweight='bold')

# Title and Legend
plt.title('Number of Events vs Period and Average Velocity vs Period', fontsize=16, fontweight='bold')
fig.legend(loc="upper left", bbox_to_anchor=(0.15, 0.85))

# Show the plot
plt.savefig('TPWT_ave_vel_num_events.png')
