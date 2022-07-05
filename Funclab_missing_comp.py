# This script converts folder name and file name to RF_input structure
from cgi import print_form
import os, obspy
import sys
import shutil

input_path = "Input"
output_path = "Output"


# #change directory to where the script is located by calling change_dir()
os.chdir(os.path.dirname(os.path.abspath(__file__)))
print('directory changed "' + os.getcwd() + '"')

# create a log file, if log is exist remove it, then create a new one
if os.path.exists("log.txt"):
    os.remove("log.txt")
log_file = open("log.txt", "w")



# source path is the folder that contains current python file
source_path = os.path.dirname(os.path.abspath(__file__))
print('source path: ' + source_path)
log_file.write('source path: ' + source_path + '\n')

# join the source path and input path
input_path = os.path.join(source_path, input_path)
print('input path: ' + input_path)
log_file.write('input path: ' + input_path + '\n')

# join the source path and output path
output_path_abs = os.path.join(source_path, output_path)
print('output path: ' + output_path_abs)

# list the folders under input path
folders = os.listdir(input_path)
#print(folders)

# loop through each folder
for folder in folders:
    #print(folder)
    # join the input path and folder name
    folder_path = os.path.join(input_path, folder)
    print('folder path: ' + folder_path)
    # list the files under the folder
    files = os.listdir(folder_path)

    # for each event, create station dictionary
    station_group = {}

    # loop through each file
    for file in files:
        #if input folder is not empty
        if files:
        #if .sac file is found, print the name of the that sac file
            if file.endswith(".sac"):
                print(file)
                log_file.write(file + '\n')
                # read the sac file with obspy
                st = obspy.read(os.path.join(folder_path, file))
                #print(st)
                for tr in st:
                    # station name from sac header
                    station = tr.stats.station
                    # year from sac header
                    year = tr.stats.starttime.year
                    # month from sac header
                    month = tr.stats.starttime.month
                    # add leading zero with zfill
                    month = str(month).zfill(2)
                    # day from sac header
                    day = tr.stats.starttime.day
                    day = str(day).zfill(2)
                    # hour from sac header
                    hour = tr.stats.starttime.hour
                    hour = str(hour).zfill(2)
                    # minute from sac header
                    minute = tr.stats.starttime.minute
                    minute = str(minute).zfill(2)
                    # second from sac header
                    second = tr.stats.starttime.second
                    second = str(second).zfill(2)
                    # get julian day from sac header
                    julian_day = tr.stats.starttime.julday
                    julian_day = str(julian_day).zfill(3)
                    print(station, julian_day ,year, month, day, hour, minute, second)
                    # write the station name, julian day, year, month, day, hour, minute, second to the log file after converting each of them to string
                    log_file.write(station + ' ' + julian_day + ' ' + str(year) + ' ' + month + ' ' + day + ' ' + hour + ' ' + minute + ' ' + second + '\n')
                    # get component from sac header
                    component = tr.stats.channel
                    print(component)
                    # get direction from each component
                    direction = component[2]
                    # write to the log file
                    log_file.write(component + '\n')
                    # get network from sac header
                    network = tr.stats.network

                    # folder name structure will be: "Event_YYYY_JJJ_HH_MM_SS" "
                    foldername = "Event_" + str(year) + "_" + str(julian_day) + "_" + str(hour) + "_" + str(minute) + "_" + str(second)
                    print('foldername: ' + foldername)

                    # file name under the folder will be: "NetworkCode.StationCode..ComponentCode.M.YYYY.MM.DD.HH.MM.SS.SAC"
                    filename = network + "." + station + "." + component + ".." + "M" + "." + str(year) + "." + str(month) + "." + str(day) + "." + str(hour) + "." + str(minute) + "." + str(second) + ".SAC"
                    print('filename: ' + filename)

                    #print(network)
                    # if station is not in the dictionary, add it
                    if station not in station_group:
                        station_group[station] = []
                        #print(station_group)
                    # if station is in the dictionary, append the file name to the list
                    if station in station_group:
                        # make sure each each component (based on the direction) is added to the list
                        if direction == 'E':
                            station_group[station].append(os.path.join(folder_path, file))
                        elif direction == 'N':
                            station_group[station].append(os.path.join(folder_path, file))
                        elif direction == 'Z':
                            station_group[station].append(os.path.join(folder_path, file))
                        else:
                            print('direction not found')
                            log_file.write('direction not found\n')

    print(station_group)
    # clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # for each station (key), each key should consists exactly 3 files
    for key in station_group:
        #print(key)
        #print(station_group[key])
        # if the length of the list is not 3, print the station name and the length of the list
        # create a different empty dictionary for the files that have 3 components
        station_group_3components = {}
        if len(station_group[key]) != 3:
            print(key, len(station_group[key]))
            log_file.write(key + ' ' + str(len(station_group[key])) + '\n')
            # create the folder if it does not exist,  move the keys to some other folder named "missing component" :The folder structure should be:
            # /missing_component/Event_YYYY_JJJ_HH_MM_SS/station_name/file_name
            if not os.path.exists(os.path.join(source_path, "missing_component")):
                os.makedirs(os.path.join(source_path, "missing_component"))
                print('missing_component folder created')
                log_file.write('missing_component folder created\n')
            else:
                print('missing_component folder already exists')
                log_file.write('missing_component folder already exists\n')
            # create folder based on Event_YYYY_JJJ_HH_MM_SS under missing_component folder
            if not os.path.exists(os.path.join(source_path, "missing_component", foldername)):
                os.makedirs(os.path.join(source_path, "missing_component", foldername))
                print('missing_component/' + foldername + ' folder created')
                log_file.write('missing_component/' + foldername + ' folder created\n')
            else:
                print('missing_component/' + foldername + ' folder already exists')
                log_file.write('missing_component/' + foldername + ' folder already exists\n')
            # try if file exists, if it does, move it to the folder, 
            # if destination file already exists, it will be overwritten
            for file in station_group[key]:
                if os.path.exists(file):
                    try:
                        shutil.move(file, os.path.join(source_path, "missing_component", foldername))
                        print(file + ' moved to missing_component/' + foldername)
                        log_file.write(file + ' moved to missing_component/' + foldername + '\n')
                    except:
                        print('error moving file')
                        log_file.write('error moving file\n')
                else:
                    print(file + ' does not exist')
                    log_file.write(file + ' does not exist\n')


