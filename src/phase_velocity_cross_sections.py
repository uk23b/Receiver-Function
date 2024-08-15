import os
import pandas as pd
import numpy as np
import pygmt
import matplotlib.pyplot as plt
from geopy.distance import geodesic
from scipy.interpolate import griddata
from pygmt.datasets import load_earth_relief

def generate_points(point1, point2, spacing_deg):
    """
    Generate points between two geographic coordinates at specified degree spacing.

    Parameters:
    - point1: tuple of (longitude, latitude) for the first point.
    - point2: tuple of (longitude, latitude) for the second point.
    - spacing_deg: spacing in degrees.

    Returns:
    - A list of tuples containing (longitude, latitude) for each point.
    """
    # Calculate the distance and the number of points needed
    distance = np.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)
    num_points = int(np.ceil(distance / spacing_deg)) + 1

    # Generate the points
    x_points = np.linspace(point1[0], point2[0], num_points)
    y_points = np.linspace(point1[1], point2[1], num_points)
    points = list(zip(x_points, y_points))
    return points

def calculate_distances(points):
    """Calculate cumulative distances between consecutive points in kilometers."""
    distances = [0]
    total_distance = 0
    for i in range(1, len(points)):
        distance = geodesic(points[i-1], points[i]).km
        total_distance += distance
        distances.append(total_distance)
    return distances

def plot_velocity_cross_section(df, point1, point2, spacing_deg=0.1, levels=np.arange(3.3, 4.4, 0.1)):
    points = generate_points(point1, point2, spacing_deg)
    distances = calculate_distances(points)
    point_tuples = [tuple(p) for p in points]
    df_filtered = df[df.apply(lambda row: (row['Lon'], row['Lat']) in point_tuples, axis=1)]

    node_indices = {pt: idx for idx, pt in enumerate(point_tuples)}
    df_filtered['Node_Index'] = df_filtered.apply(lambda row: node_indices[(row['Lon'], row['Lat'])], axis=1)

    node_idx_array = np.array(distances)
    period_values = np.sort(df_filtered['Period'].unique())
    period_grid, distance_grid = np.meshgrid(period_values, node_idx_array, indexing='ij')

    velocity_grid = griddata(
        (df_filtered['Period'], df_filtered['Node_Index']), df_filtered['Velocity'],
        (period_grid, distance_grid), method='cubic'
    )

    plt.figure(figsize=(14, 8))
    cp = plt.contourf(distance_grid, period_grid, velocity_grid, levels=levels, cmap='viridis', extend='both')
    contour_lines = plt.contour(distance_grid, period_grid, velocity_grid, levels=levels, colors='black', linewidths=0.5)
    plt.clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')
    cbar = plt.colorbar(cp, ticks=levels, label='Velocity (km/s)')
    cbar.ax.set_yticklabels(['{:.1f}'.format(vel) for vel in levels])

    plt.xlabel('Distance along profile (km)')
    plt.ylabel('Period (s)')
    plt.gca().invert_yaxis()
    plt.title('Seismic Velocity Cross-Section with Contour Lines')

    # Set plot limits if necessary
    plt.xlim([distance_grid.min(), distance_grid.max()])
    plt.ylim([period_grid.min(), period_grid.max()])

    # Adjust the aspect of the plot if necessary
    plt.gca().set_aspect('auto')

    # Save the figure
    plt.tight_layout()  # Adjust the padding of the figure
    plt.savefig(f'velocity_cross_section_{points[0][0]}_{points[-1][0]}_{points[0][1]}_{points[-1][1]}.png')


def bilinear_interpolation(df, point, spacing_deg=0.1):
    x, y = point
    # Define grid boundaries for bilinear interpolation
    x_floor, x_ceil = np.floor(x / spacing_deg) * spacing_deg, np.ceil(x / spacing_deg) * spacing_deg
    y_floor, y_ceil = np.floor(y / spacing_deg) * spacing_deg, np.ceil(y / spacing_deg) * spacing_deg

    # Fetch the velocities at these boundary points
    def get_velocity_at(lon, lat):
        # Handle cases where point may fall outside the DataFrame bounds
        subset = df[(df['Lon'].between(lon-0.01, lon+0.01)) & (df['Lat'].between(lat-0.01, lat+0.01))]
        if not subset.empty:
            return subset.iloc[0]['Velocity']
        return np.nan

    V00 = get_velocity_at(x_floor, y_floor)
    V10 = get_velocity_at(x_ceil, y_floor)
    V01 = get_velocity_at(x_floor, y_ceil)
    V11 = get_velocity_at(x_ceil, y_ceil)

    # Bilinear interpolation formula
    if not np.isnan([V00, V10, V01, V11]).any():
        # Interpolate in x-direction
        Vx0 = (x_ceil - x) / spacing_deg * V00 + (x - x_floor) / spacing_deg * V10
        Vx1 = (x_ceil - x) / spacing_deg * V01 + (x - x_floor) / spacing_deg * V11

        # Interpolate in y-direction
        Vy = (y_ceil - y) / spacing_deg * Vx0 + (y - y_floor) / spacing_deg * Vx1
        return Vy
    return np.nan




def process_TPWT_ANT_files(main_input_path):
    # script path
    script = os.path.abspath(__file__)
    # script directory
    script_dir = os.path.dirname(script)
    # change directory to the script directory
    os.chdir(script_dir)

    TPWT_folder = 'TPWT'
    ANT_folder = 'ANT'  
    TPWT_folder_path = os.path.join(main_input_path, TPWT_folder)
    ANT_folder_path = os.path.join(main_input_path, ANT_folder)
    TPWT_files = os.listdir(TPWT_folder_path)
    TPWT_files.sort()
    ANT_files = os.listdir(ANT_folder_path)
    ANT_files.sort()

    # create a list to store period values, lon, lat, and velocity values
    all_values = []

    # loop over TPWT files
    for i in TPWT_files:
        # split the file name by dot
        file_name = i.split('.')
        # get the second part of the file name
        freq = (file_name[1])
        freq = '0.' + freq
        period = round(1/float(freq))  
        # read the TPWT file
        TPWT_file = os.path.join(TPWT_folder_path, i)
        TPWT_data = pd.read_csv(TPWT_file, sep='\s+', header=None)
        # first column is lon, second column is lat, third column is velocity
        lon = TPWT_data.iloc[:,0].values
        lat = TPWT_data.iloc[:,1].values
        vel = TPWT_data.iloc[:,2].values
        period = [period] * len(lon)
        # create tuples of lon, lat, and velocity
        values = list(zip(period, lon, lat, vel))
        # append the values to all_values list
        all_values.extend(values)

    # loop over ANT files
    for i in ANT_files:
        # split the file name by dot
        file_name = i.split('.')
        # get the second part of the file name
        freq = (file_name[1])
        #print('freq:', freq)
        freq = '0.' + freq
        period = round(1/float(freq))  
        # read the ANT file
        ANT_file = os.path.join(ANT_folder_path, i)
        ANT_data = pd.read_csv(ANT_file, sep='\s+', header=None)
        # first column is lon, second column is lat, third column is velocity
        lon = ANT_data.iloc[:,0].values
        lat = ANT_data.iloc[:,1].values
        vel = ANT_data.iloc[:,2].values
        period = [period] * len(lon)
        # create tuples of lon, lat, and velocity
        values = list(zip(period, lon, lat, vel))
        # append the values to all_values list
        all_values.extend(values)

    # create a dataframe from all_values list
    df = pd.DataFrame(all_values, columns=['Period', 'Lon', 'Lat', 'Velocity'])
    # write to a csv file
    df.to_csv(os.path.join(main_input_path, 'TPWT_ANT_all_values.csv'), index=False)

    return df



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

def plot_seismic_velocity(node_idx_grid, period_grid, velocity_grid, points, ax):
    levels = np.arange(3.3, 4.4, 0.1)
    cp = ax.contourf(node_idx_grid, period_grid, velocity_grid, levels=levels, cmap='viridis', extend='both')
    contour_lines = ax.contour(node_idx_grid, period_grid, velocity_grid, levels=levels, colors='black', linewidths=0.5)
    ax.clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')
    cbar = plt.colorbar(cp, ax=ax, ticks=levels, label='Velocity (km/s)')
    cbar.ax.set_yticklabels(['{:.1f}'.format(vel) for vel in levels])

    x_axis_is_lat = np.allclose(points[:, 0], points[0, 0], atol=1e-6)
    x_labels = points[:, 1] if x_axis_is_lat else points[:, 0]
    x_label = 'Latitude' if x_axis_is_lat else 'Longitude'

    tick_indices = np.where(np.isclose(x_labels % 0.5, 0, atol=1e-2))[0]
    ax.set_xticks(tick_indices)
    ax.set_xticklabels(["{:.2f}".format(x_labels[idx]) for idx in tick_indices])
    ax.set_xlabel(x_label)
    ax.set_ylabel('Period (s)')
    ax.invert_yaxis()
    ax.set_title('Seismic Velocity Cross-Section with Contour Lines')

def plot_elevation_profile(line_with_elevation_df):
    distances = np.sqrt(np.diff(line_with_elevation_df['longitude'])**2 + np.diff(line_with_elevation_df['latitude'])**2) * 111.32
    cumulative_distance = np.insert(np.cumsum(distances), 0, 0)
    plt.plot(cumulative_distance, line_with_elevation_df['elevation'], linestyle='-', color='black')
    plt.xlabel('Distance Along Profile (km)')
    plt.ylabel('Elevation (m)')
    plt.title('Elevation Profile')

main_input_path = '/Users/utkukocum/Desktop/RF_Surf/final25/Dispersion_Grid_Files'

def main():
    main_input_path = '/Users/utkukocum/Desktop/RF_Surf/final25/Dispersion_Grid_Files'
    df = process_TPWT_ANT_files(main_input_path)
    
    df_filtered = df[(df['Period'] >= 0) & (df['Period'] <= 143)]

    min_vel = 2.3
    max_vel = 3.8

    velocity_levels = np.arange(df_filtered['Velocity'].min(), df_filtered['Velocity'].max() + 0.1, 0.1)
    #velocity_levels = np.arange(min_vel, max_vel + 0.1, 0.1)
    contour_levels = np.linspace(df_filtered['Velocity'].min(), df_filtered['Velocity'].max(), num=8)  # Less contour lines

    point1 = [46.5, 39.6] # [longitude, latitude]
    point2 = [44.3, 42.5] # [longitude, latitude]
    spacing_deg = 0.001

    points = generate_points(point1, point2, spacing_deg)

    grid = load_earth_relief(resolution="30s", region=[36, 52, 36, 45])

    # # Plotting the elevation profile
    fig, ax1 = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [1, 3]})

    # Plot elevation profile
    ax1[0].plot(create_line_with_elevation(point1, point2, spacing_deg, grid))
    ax1[0].set_ylabel('Elevation (m)')
    ax1[0].legend()
    ax1[0].set_xlabel('Distance Along Profile (km)', fontsize=18, fontweight='bold')
    ax1[0].set_ylabel('Elevation (m)', fontsize=18, fontweight='bold')
    # set xticks size and bold
    ax1[0].tick_params(axis='x', labelsize=16, width=2)
    # set yticks size and bold
    ax1[0].tick_params(axis='y', labelsize=16, width=2)
    ax1[0].grid(True)
    ax1[0].set_title('Elevation Profile', fontsize=18, fontweight='bold')

    # Plot seismic velocity cross-section
     #Define the step for x-axis ticks as 0.5 degrees
    x_tick_step = 0.5
    tick_indices = [i for i, pt in enumerate(points) if pt[1 if point1[0] == point2[0] else 0] % x_tick_step < 0.01]
    tick_labels = [f"{pt[1 if point1[0] == point2[0] else 0]:.1f}" for i, pt in enumerate(points) if i in tick_indices]
#     # Calculate the indices for the x-ticks based on the tick step
#     tick_indices = [i for i, pt in enumerate(points) if pt[1 if point1[0] == point2[0] else 0] % x_tick_step < 0.01]
#     tick_labels = [f"{pt[1 if point1[0] == point2[0] else 0]:.1f}" for i, pt in enumerate(points) if i in tick_indices]

    # Define velocity levels for contouring and coloring
    velocity_levels = np.arange(df_filtered['Velocity'].min(), df_filtered['Velocity'].max() + 0.1, 0.1)
    contour_levels = np.linspace(df_filtered['Velocity'].min(), df_filtered['Velocity'].max(), num=8)  # Less contour lines


    plt.subplot(2, 1, 2)  # This is the seismic velocity plot
    points = generate_points(point1, point2, spacing_deg)
    distances = calculate_distances(points)
    period_values = np.sort(df_filtered['Period'].unique())
    velocity_grid = np.zeros((len(period_values), len(distances)))
    for i, period in enumerate(period_values):
        df_period = df_filtered[df_filtered['Period'] == period]
        velocity_values = griddata((df_period['Lon'], df_period['Lat']), df_period['Velocity'], points, method='cubic')
        velocity_grid[i, :] = velocity_values

    cp = ax1[1].contourf(distances, period_values, velocity_grid, levels=velocity_levels, cmap='viridis', extend='both')
    contour_lines = ax1[1].contour(distances, period_values, velocity_grid, levels=velocity_levels, colors='black', linewidths=0.5)
    ax1[1].clabel(contour_lines, inline=True, fontsize=8, fmt='%.1f')

    # Creating a horizontal color bar
    cbar = plt.colorbar(cp, ax=ax1[1], orientation='horizontal', pad=0.1, aspect=40)
    cbar.set_label('Velocity (km/s)')
    # cbar.set_ticks(np.linspace(velocity_levels.min(), velocity_levels.max(), num=len(contour_levels)))
    cbar.set_ticks(np.linspace(velocity_levels.min(), velocity_levels.max(), num=len(contour_levels)))
    cbar.ax.set_xticklabels(['{:.1f}'.format(vel) for vel in np.linspace(velocity_levels.min(), velocity_levels.max(), num=len(contour_levels))])

    ax1[1].set_xlabel('Distance along profile (km)', fontsize=18, fontweight='bold')
    ax1[1].set_ylabel('Period (s)', fontsize=18, fontweight='bold')
    ax1[1].invert_yaxis()
    ax1[1].set_title(f'Seismic Velocity Cross-Section from {point1} to {point2}', fontsize=18, fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(main_input_path, f'cross_section_{point1[0]}_{point1[1]}_{point2[0]}_{point2[1]}.png'))
    print('Path is:', os.path.join(main_input_path, f'cross_section_{point1[0]}_{point1[1]}_{point2[0]}_{point2[1]}.png'))

if __name__ == '__main__':
    main()
