import os
import obspy
import sys
import glob
import pandas as pd


file = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/stations_info_main_database2.xlsx'
# Read excel file
df = pd.read_excel(file, sheet_name='all')

# Assign variables to the columns
station_name = df.iloc[:, 0]
network_name = df.iloc[:, 1]
latitude = df.iloc[:, 2]
longitude = df.iloc[:, 3]

# Create dictionary for each station
stations_dict = {}
for i in range(len(station_name)):
    key = station_name[i]
    value = [network_name[i], latitude[i], longitude[i]]
    stations_dict[key] = value


# main path event folders that contain sac files for each component
main_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/decimated/'
# list of folders
folders = os.listdir(main_path)

for folder in tqdm(folders, desc='Processing Folders'):
    # path to event folder
    folder_path = os.path.join(main_path, folder)
    # list of sac files
    files = glob.glob(folder_path + '/*.SAC')

    for file in tqdm(files, desc=f'Processing Files in {folder}', leave=False):
        # read sac file
        st = obspy.read(file)
        # get station name
        station = st[0].stats.station
        
        # Check if station name is in the dictionary
        if station in stations_dict:
            # Update latitude and longitude attributes of st
            st[0].stats.sac['stla'] = stations_dict[station][1]
            st[0].stats.sac['stlo'] = stations_dict[station][2]
            
            # Get the original file path and name
            file_path, file_name = os.path.split(file)
            
            # Construct the new file path with the updated data
            new_file = os.path.join(file_path, file_name)
            
            # Write the updated st object to the new file
            st.write(new_file, format='SAC')
