import os
import glob
import obspy
import numpy as np
import pandas as pd
import shutil

main_sta_lta_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/sta_lta_out2.txt'
# read the file
df = pd.read_csv(main_sta_lta_path, sep='\t', header=None)
# convert the dataframe to numpy array
data = df.values

all_info = []
all_info_no_sta_lta = []

# length of each list in data
for row in data:
    # get the first item of each row
    file_path = row[0]
    # split the file path by '/' and get the last item
    file_name = file_path.split('/')[-1]
    file_name_main = file_name.split(' ')[0]
    file_name_main_split = file_name_main.split('.')
    year = file_name_main_split[5]
    year = str(year)
    station_name = file_name_main_split[1]
    network_name = file_name_main_split[0]
    component = file_name_main_split[2]
    direction = component[2]
    month = file_name_main_split[6]
    month = str(month)
    month = month.zfill(2)
    day = file_name_main_split[7]
    day = str(day)
    day = day.zfill(2)
    hour = file_name_main_split[8]
    hour = str(hour)
    hour = hour.zfill(2)
    minute = file_name_main_split[9]
    minute = str(minute)
    minute = minute.zfill(2)
    second = file_name_main_split[10]
    second = str(second)
    second = second.zfill(2)

    # get the sta/lta value
    sta_lta = file_name.split(' ')[1]
    sta_lta = float(sta_lta)

    # create tuple of combined data
    combined_data = (year, station_name, direction, hour, minute, sta_lta)
    combined_data_no_sta_lta = (year, station_name, direction, hour, minute)
    # append the tuple to the list
    all_info.append(combined_data)
    all_info_no_sta_lta.append(combined_data_no_sta_lta)

# get the only direction name = 'Z' from all_info and all_info_no_sta_lta
all_info_Z = [row for row in all_info if row[2] == 'Z']
all_info_no_sta_lta_Z = [row for row in all_info_no_sta_lta if row[2] == 'Z']

# path to data folder
data_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/decimated_done/'
# list of folders
folders = os.listdir(data_path)

# loop through the folders
for folder in folders:
    # path to event folder
    folder_path = os.path.join(data_path, folder)
    # list of sac files
    files = glob.glob(folder_path + '/*.SAC')
    # loop through the files
    for file in files:
        # read sac file
        st = obspy.read(file)
        # station longitude and latitude
        stla = st[0].stats.sac.stla
        stlo = st[0].stats.sac.stlo
        # station name
        sta = st[0].stats.sac.kstnm
        # get the year and julian day
        year_data = st[0].stats.sac.nzyear
        julian_day_data = st[0].stats.sac.nzjday
        year_data = str(year_data)
        julian_day_data = str(julian_day_data)
        julian_day_data = julian_day_data.zfill(3)
        # get the hour and minute
        hour_data = st[0].stats.sac.nzhour
        hour_data = str(hour_data)
        hour_data = hour_data.zfill(2)
        minute_data = st[0].stats.sac.nzmin
        minute_data = str(minute_data)
        minute_data = minute_data.zfill(2)
        # get the component
        component = st[0].stats.sac.kcmpnm
        direction = component[2]
        if direction == 'N' or direction == 'E':  # skip the north and east components
            continue
        # create tuple from data in the similar format as the data in all_info
        data_match = (year_data, sta, direction, hour_data, minute_data)
        if data_match in all_info_no_sta_lta_Z:
            # then get the sta/lta value if sta/lta value is less than 1.1, then we can move this data
            # get the index of the data_match in all_info_no_sta_lta_Z
            index = all_info_no_sta_lta_Z.index(data_match)
            # get the sta/lta value
            sta_lta = all_info_Z[index][-1]
            # convert the sta/lta value to float
            sta_lta = float(sta_lta)
            if sta_lta < 1.1:
                new_folder = os.path.join('less_than_1-1', folder)
                print('Moving:', file)
                os.makedirs(new_folder, exist_ok=True)
                for component_file in glob.glob(os.path.join(folder_path, f'*{sta}*')):
                    destination_file = os.path.join(new_folder, os.path.basename(component_file))
                    if not os.path.exists(destination_file):
                        shutil.move(component_file, new_folder)
                    else:
                        print('Destination file already exists. Skipping:', component_file)