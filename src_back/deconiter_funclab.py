import obspy,os
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
import matplotlib.pyplot as plt
from obspy.geodetics import kilometers2degrees
from obspy.taup import TauPyModel
import numpy as np
import seispy
from obspy.taup import TauPyModel
from decon import deconit as deconiti
import gc
import shutil

# Define the main folder and output folder paths
main_folder = '/Volumes/UNTITLE/decimated_dn_1.0/'
output_folder = '/Volumes/UNTITLE/decimated_dn_1.0_rotated/'

# Define the constant gauss value
gauss = 1.0

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# List event folders under the main folder
event_folders = [f for f in os.listdir(main_folder) if os.path.isdir(os.path.join(main_folder, f))]

# Sort the event folders
event_folders.sort()

# Loop over event folders
for event_folder in event_folders:
    # Create corresponding subdirectories in the output folder
    output_event_folder = os.path.join(output_folder, event_folder)
    os.makedirs(output_event_folder, exist_ok=True)

    # List files under the event folder
    event_files = os.listdir(os.path.join(main_folder, event_folder))
    
    print(f"Processing event folder: {event_folder}")

    # Create a dictionary to store files grouped by station name for the current event folder
    station_files_dict = {}

    # Loop over files under the event folder
    for file_name in event_files:
        # Check if the file ends with ".SAC"
        if file_name.endswith(".SAC"):
            # Split the file name by the dot (assuming it follows the format "network.station.component.SAC")
            file_parts = file_name.split('.')
            
            network = file_parts[0]
            station_name = file_parts[1]

            # File path
            file_path = os.path.join(main_folder, event_folder, file_name)

            # Append file path to the dictionary
            if (network, station_name) not in station_files_dict:
                station_files_dict[(network, station_name)] = []
            station_files_dict[(network, station_name)].append(file_path)

    # Loop over network and station names in the dictionary
    for (network, station_name) in station_files_dict:
        # Read the files for each network and station with obspy
        wave_stream_station = obspy.Stream()
        for file_path in station_files_dict[(network, station_name)]:
            wave_stream_station += obspy.read(file_path)

        # Get evla, evlo, stla, stlo for bazi calculation
        evla = wave_stream_station[0].stats.sac.evla
        evlo = wave_stream_station[0].stats.sac.evlo
        stla = wave_stream_station[0].stats.sac.stla
        stlo = wave_stream_station[0].stats.sac.stlo

        # Calculate the back azimuth (bazi) and distance (dist)
        da = seispy.distaz(evla, evlo, stla, stlo)
        bazi = da.baz
        dist = da.delta

        # Sort the wave stream by channel
        wave_stream_station.sort(keys=['channel'], reverse=True)

        #trim the data to have the same time span for rotation from NE to RT
        wave_stream_station.trim(max(tr.stats.starttime for tr in wave_stream_station), min(tr.stats.endtime for tr in wave_stream_station))

        # Rotate the wave stream
        wave_stream_station.rotate(method='NE->RT', back_azimuth=bazi)

        # Extract r, t, z components
        wave_stream_r = wave_stream_station.select(component='R')
        wave_stream_t = wave_stream_station.select(component='T')
        wave_stream_z = wave_stream_station.select(component='Z')

        # Create the output subdirectory for the station (inside the event folder)


        # Write the rotated files to output folder with filename convention: network_station_gauss.i.r/t/z
        output_file_r = os.path.join(output_event_folder, f"{network}_{station_name}_{gauss}.i.r")
        output_file_t = os.path.join(output_event_folder, f"{network}_{station_name}_{gauss}.i.t")
        output_file_z = os.path.join(output_event_folder, f"{network}_{station_name}_{gauss}.i.z")

        wave_stream_r.write(output_file_r, format='SAC')
        wave_stream_t.write(output_file_t, format='SAC')
        wave_stream_z.write(output_file_z, format='SAC')

        # Copy the original files to the output folder (inside the event folder)
        for file_path in station_files_dict[(network, station_name)]:
            shutil.copy(file_path, output_event_folder)

        # 
        #model = TauPyModel(model='ak135')

