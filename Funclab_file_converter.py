# RF data format to FUNCLAB data format converter
import sys, os, time, struct, math, obspy

# source folder path
Input = "Input" # Input folder path
Output = "Output_test" # Output folder path

script_name = sys.argv[0] # source file path, sys.argv[0] is the script name, sys.argv[1] is the source file path
print("Source path: " + script_name)
source_path = '/Volumes/UNTITLED/14_File_Format_Conversion_FUNCLAB'

# define a function read obspy data under certain folder structure


# join script directory and source folder path (Input)

#Input_path = os.path.join(os.path.dirname(script_name), Input)
Input_path = os.path.join(source_path,Input)
#print("Input path: " + Input_path)

# list all files in the Input_path
Input_RF_files = os.listdir(Input_path)
#print("Input RF files: " + str(Input_RF_files))

st_list = []

# if the files type is folder in Input_RF_files, the script will list all files in the folder
for i in range(len(Input_RF_files)):
    if os.path.isdir(os.path.join(Input_path, Input_RF_files[i])):
        folder_path = os.path.join(Input_path, Input_RF_files[i])
        Input_RF_files[i] = os.listdir(os.path.join(Input_path, Input_RF_files[i]))
        # clear st_list
        st_list.clear()
        for j in range(len(Input_RF_files[i])):
            Input_RF_files[i][j] = os.path.join(folder_path, Input_RF_files[i][j])
            Input_file_path = Input_RF_files[i][j]
            #print("Input file path: " + Input_file_path)
            # read with obspy
            st = obspy.read(Input_file_path)
            #print("Input file info: " + str(st))
            st_list.append(st)


# create a list from return value of read_obspy_data() and append to st_list



        for tr in st_list:
            print(tr)
            # station name and channel name
            station_name = tr[0].stats.station
            channel_name = tr[0].stats.channel
            print("Station name: " + station_name)
            print("Channel name: " + channel_name)

            # if last two characters of channel name ends with "NZ", change it to "HZ"
            if channel_name[-2:] == "NZ":
                channel_name_str = channel_name[:-2] + "HZ"
                print("Channel name: " + channel_name_str + " converted")
                tr[0].stats.channel = channel_name_str # change channel name

            if channel_name[-2:] == "NE":
                channel_name_str = channel_name[:-2] + "HE"
                print("Channel name: " + channel_name_str + " converted")
                tr[0].stats.channel = channel_name_str # change channel name

            if channel_name[-2:] == "NN":
                channel_name_str = channel_name[:-2] + "HN"
                print("Channel name: " + channel_name_str + " converted")
                tr[0].stats.channel = channel_name_str # change channel name

            print(tr[0].stats.channel)

            # get sampling rate
            sampling_rate = tr[0].stats.sampling_rate

            # if sampling rate is bigger than 5
            if sampling_rate > 5:

                # network name
                network_name = tr[0].stats.network
                # year from sac header
                year = tr[0].stats.starttime.year
                # month from sac header
                month = tr[0].stats.starttime.month
                month = str(month).zfill(2)
                # day from sac header
                day = tr[0].stats.starttime.day
                day = str(day).zfill(2)
                # hour from sac header
                hour = tr[0].stats.starttime.hour
                hour = str(hour).zfill(2)
                # minute from sac header
                minute = tr[0].stats.starttime.minute
                minute = str(minute).zfill(2)
                # second from sac header
                second = tr[0].stats.starttime.second
                second = str(second).zfill(2)
                # get julian day
                julian_day = tr[0].stats.starttime.julday
                julian_day = str(julian_day).zfill(3)
                # get direction from each component
                direction = tr[0].stats.channel[2]
                print("Direction: " + direction)

                # get event start time from sac header
                event_start_time = tr[0].stats.starttime
                # trim the data to the event start time if event start time is different from the data start time
                if event_start_time != tr[0].stats.sac.b:
                    tr[0].trim(starttime=event_start_time)

                # folder name structure will be: "Event_YYYY_JJJ_HH_MM_SS" "
                Funclab_foldername = "Event_" + str(year) + "_" + str(julian_day) + "_" + str(hour) + "_" + str(minute) + "_" + str(second)
                print('foldername: ' + Funclab_foldername)

                # create a output folder path if not exist
                if not os.path.exists(os.path.join(os.path.dirname(script_name), Output, Funclab_foldername)):
                    os.makedirs(os.path.join(os.path.dirname(script_name), Output, Funclab_foldername))
                # join script directory and output folder path (Output)
                Output_folder_path = os.path.join(os.path.dirname(script_name), Output, Funclab_foldername)
                print("Output folder path: " + Output_folder_path)

                # file name under the folder will be: "NetworkCode.StationCode..ComponentCode.M.YYYY.MM.DD.HH.MM.SS.SAC"
                filename_Funclab = network_name + "." + station_name + "." + tr[0].stats.channel + ".." + "M" + "." + str(year) + "." + str(month) + "." + str(day) + "." + str(hour) + "." + str(minute) + "." + str(second) + ".SAC"
                print('filename: ' + filename_Funclab)
                # join output folder path and file name
                Output_file_path = os.path.join(Output_folder_path, filename_Funclab)
                # write to output file
                tr.write(Output_file_path, format="SAC")
    #


    











