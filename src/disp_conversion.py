import os,sys,math
import numpy as np
import matplotlib.pyplot as plt

input_period_list = [5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,50,67,80,100,111,143]

error = 0.005

out_disp_folder = 'dispersion_output'

# get the script directory
script_dir = os.path.dirname(os.path.realpath(__file__))
print(script_dir)
# change the working directory to the script directory
os.chdir(script_dir)

folder_name = 'final25'
disp_files_folder = 'Dispersion_Grid_Files'

data_folder_name = ['ANT', 'TPWT']
 
# join the folder name to the script directory
folder_path = os.path.join(script_dir, folder_name)

# list the files in the folder
file_list = os.listdir(folder_path)
print(file_list)

# join the dispersion files folder name to the folder path
disp_files_folder_path = os.path.join(folder_path, disp_files_folder)
disp_out_folder_path = os.path.join(folder_path, out_disp_folder)

# list the files in the dispersion files folder
disp_files_list = os.listdir(disp_files_folder_path)
print(disp_files_list)

# join the disp_files_folder_path to the data_folder_name
data_folder_path_ANT = os.path.join(disp_files_folder_path, data_folder_name[0])
data_folder_path_TPWT = os.path.join(disp_files_folder_path, data_folder_name[1])

# list the files in the data folder
data_files_list_ANT = os.listdir(data_folder_path_ANT)
data_files_list_TPWT = os.listdir(data_folder_path_TPWT)

# sort the files in the data folder
data_files_list_ANT.sort()
data_files_list_TPWT.sort()

# reverse the list
data_files_list_ANT.reverse()
data_files_list_TPWT.reverse()

# skip hidden files
data_files_list_ANT = [f for f in data_files_list_ANT if not f[0] == '.']
data_files_list_TPWT = [f for f in data_files_list_TPWT if not f[0] == '.']

print(data_files_list_ANT)
print(data_files_list_TPWT)

# join the data_folder_path to the data_files_list
data_file_path_ANT = [os.path.join(data_folder_path_ANT, f) for f in data_files_list_ANT]
data_file_path_TPWT = [os.path.join(data_folder_path_TPWT, f) for f in data_files_list_TPWT]


# receiver function part
CCPtoRFs = 'CCPtoRFs'
CCPtoRFs_OUTPUTs = 'OUTPUTs'
CCPtoRFs_folder_path = os.path.join(folder_path, CCPtoRFs)
CCPtoRFs_OUTPUTs_folder_path = os.path.join(CCPtoRFs_folder_path, CCPtoRFs_OUTPUTs)

# list only .sac files in the CCPtoRFs_OUTPUTs folder 
CCPtoRFs_OUTPUTs_files_list = [f for f in os.listdir(CCPtoRFs_OUTPUTs_folder_path) if f.endswith('.sac')]
CCPtoRFs_OUTPUTs_files_list.sort()

# skip hidden files
CCPtoRFs_OUTPUTs_files_list = [f for f in CCPtoRFs_OUTPUTs_files_list if not f[0] == '.']

input_coord_list = []

# loop through the files in CCPtoRFs_OUTPUTs folder
for f in CCPtoRFs_OUTPUTs_files_list:
    print(f)
    # split the file name by '.'
    f_split = f.split('_')
    longitude = f_split[1]
    latitude = f_split[2]
    # remove the '.sac' from latitude
    latitude = latitude[:-4]
    print(longitude, latitude)
    # create pair of longitude and latitude
    lon_lat = (longitude, latitude)
    # append the pair to the input coordinate list
    input_coord_list.append(lon_lat)




# read synthetic receiver function coordinates from the folder

# loop through the data files
for i in range(len(data_file_path_ANT)):
    print(data_files_list_ANT[i])
    # split the file name by dot
    file_name_split = data_files_list_ANT[i].split('.')
    frequency = file_name_split[1]
    print(frequency)
    # update frequency by add 0. to the front
    frequency = '0.' + frequency
    print(frequency)
    period = 1./float(frequency)
    # round up or down the period to the nearest integer
    period = round(period)
    print(period)

    # read the data file
    data_ANT = np.loadtxt(data_file_path_ANT[i])
    print(data_ANT.shape)

    # read each column of the data file
    lon_ANT = data_ANT[:,0]
    lat_ANT = data_ANT[:,1]
    vel_ANT = data_ANT[:,2]

    # do the same for TPWT, if index is out of range, skip
    try:
        data_TPWT = np.loadtxt(data_file_path_TPWT[i])
        print(data_TPWT.shape)
        lon_TPWT = data_TPWT[:,0]
        lat_TPWT = data_TPWT[:,1]
        vel_TPWT = data_TPWT[:,2]

        # get frequency information from the file name for TPWT
        file_name_split = data_files_list_TPWT[i].split('.')
        frequency_TPWT = file_name_split[1]
        print(frequency_TPWT)
        # update frequency by add 0. to the front
        frequency_TPWT = '0.' + frequency_TPWT
        print(frequency_TPWT)
        period_TPWT = 1./float(frequency_TPWT)
        # round up or down the period to the nearest integer
        period_TPWT = round(period_TPWT)
        print(period_TPWT)

        
    except IndexError:
        pass



    # loop through the input coordinate list
    for j in range(len(input_coord_list)):
        # get the input coordinate
        input_coord = input_coord_list[j]
        print(input_coord)
        # get the longitude and latitude from the input coordinate
        input_lon = input_coord[0]
        input_lat = input_coord[1]
        # convert the longitude and latitude to float
        input_lon = float(input_lon)
        input_lat = float(input_lat)
        print(input_lon, input_lat)
        # find the index of the input coordinate in the data file
        index = np.where((lon_ANT == input_lon) & (lat_ANT == input_lat))

        # same for TPWT
        try:
            index_TPWT = np.where((lon_TPWT == input_lon) & (lat_TPWT == input_lat))
            print('index TPWT is: ',index_TPWT)
            vel_TPWT_input = vel_TPWT[index_TPWT]
            print('vel TPWT input is: ',vel_TPWT_input)

            #convert the velocity to string
            vel_TPWT_input = str(vel_TPWT_input)
            # remove the brackets
            vel_TPWT_input = vel_TPWT_input[1:-1]
            print('vel TPWT input is: ',vel_TPWT_input)

            # split the velocity by space
            vel_TPWT_input_split = vel_TPWT_input.split(' ')
            print('vel TPWT input split is: ',vel_TPWT_input_split)


            # get the period and velocity from the input coordinate
            # period_vel = input_coord + (period, vel)
            period_vel_TPWT = (period_TPWT, vel_TPWT_input_split[0])
            # period_vel_TPWT = (period, vel_TPWT_input_split[0])






        except NameError:
            pass

        


        print(index)
        # get the velocity at the index (ANT)
        vel = vel_ANT[index]
        print(vel)
        # convert the velocity to string
        vel = str(vel)
        # remove the '[' and ']' from the velocity
        vel = vel[1:-1]
        print(vel)
        # split the velocity by space
        vel_split = vel.split()
        print(vel_split)
        # get the first element of the split velocity
        vel = vel_split[0]
        print(vel)
        # get the period and velocity from the input coordinate
        period_vel = input_coord + (period, vel)
        print(period_vel)

        # if period information is both in ANT and in TPWT, append only TPWT, skip ANT

        try:
            if period_vel_TPWT[0] == period_vel[0]:
                print('period_vel_TPWT is: ',period_vel_TPWT)
                print('period_vel is: ',period_vel)
                period_vel = period_vel_TPWT
                print('period_vel is: ',period_vel)
                # get the velocity information for only TPWT, skip ANT
                vel = period_vel[3]
                print('vel is: ',vel)
                # convert the velocity to float
                vel = float(vel)
                print('vel is: ',vel)
                
        except NameError:
            pass

        # convert the velocity to float
        vel = float(vel)
        print(vel)
        





        # create output dispersion folder if not exist
        if not os.path.exists(disp_out_folder_path):
            os.makedirs(disp_out_folder_path)

        # create output dispersion file name (filename format: pv.lon_lat)
        # format the longitude and latitude to '%.3f' 
        disp_out_file_name = 'pv.' + '%.3f' % (input_lon) + '_' + '%.3f' % (input_lat)
        # disp_out_file_name = 'pv.' + str(input_lon) + '_' + str(input_lat)

        # create output dispersion file path
        disp_out_file_path = os.path.join(disp_out_folder_path, disp_out_file_name)

        # content of the file will 'SURF96 R C X 0 period velocity' (with new line)
        # format of period and velocity is '%.2f' and '%.3f'


        disp_out_content = 'SURF96 R C X 0 ' + '%.2f' % float(period) + ' ' + '%.3f' % float(vel) + ' '  + str(error) + '\n'

        # create disp_out_content for TPWT
        try:
            disp_out_content_TPWT = 'SURF96 R C X 0 ' + '%.2f' % float(period_TPWT) + ' ' + '%.3f' % float(vel_TPWT_input_split[0]) + ' '  + str(error) +'\n'
        except NameError:
            pass


        # write the content to the output file with increasing period order
        if period <= 40:
        # if period information is both in ANT and in TPWT, append only TPWT, skip ANT
            try:
                if period_TPWT == period:
                    with open(disp_out_file_path, 'a') as disp_out_file:
                        disp_out_file.write(disp_out_content_TPWT)
                        disp_out_file.write(disp_out_content)
                else:
                    with open(disp_out_file_path, 'a') as disp_out_file:
                        disp_out_file.write(disp_out_content)
            except NameError:
                with open(disp_out_file_path, 'a') as disp_out_file:
                    disp_out_file.write(disp_out_content)
        else:
            with open(disp_out_file_path, 'a') as disp_out_file:
                disp_out_file.write(disp_out_content_TPWT)
        
        if period_TPWT > 40:
            disp_out_content_TPWT = 'SURF96 R C X 0 ' + '%.2f' % float(period_TPWT) + ' ' + '%.3f' % float(vel_TPWT_input_split[0]) + ' '   + str(error) +'\n'
            with open(disp_out_file_path, 'a') as disp_out_file:
                disp_out_file.write(disp_out_content_TPWT)

        # close the output file
        disp_out_file.close()



            



        

       


        # # print the output file path
        # print(disp_out_file_path)
        

        #disp_out_content = 'SURF96 R C X 0 ' + str(period) + ' ' + str(vel) + '\n'

        # # if the output file does not exist, create the file and write the content
        # if not os.path.exists(disp_out_file_path):
        #     with open(disp_out_file_path, 'w') as f:
        #         f.write(disp_out_content)
        # # if the output file exist, append the content to the file 
        # else:
        #     with open(disp_out_file_path, 'a') as f:
        #         f.write(disp_out_content)

        # close the file
       #f.close()


        



