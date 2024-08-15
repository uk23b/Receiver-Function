import os,sys
import numpy as np
import pandas as pd
import subprocess
import obspy
import shutil

# main path that contains all the raw data.
main_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/decimated_done'
#main_path = '/Users/utkukocum/icloud/Joint_test/decimated_done'
main_path_p = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB'
#main_path_p = '/Users/utkukocum/icloud/Joint_test'


# cut script
cut_name = 'DOCUT1'

# decon script
decon_name = 'DODECON'

# Decon folder
decon_folder = 'DECON'


# rotated files
rotated_files = '/Volumes/UNTITLE/17_Hermann/test40/RAWDATA/'
#rotated_files = '/Users/utkukocum/icloud/Joint_test/RAWDATA/'
print(rotated_files)

# list all the folders
folders = os.listdir(rotated_files)
# sort folders
folders.sort()
print(folders)

rftn_target ='2.5'
target_alpha = rftn_target

alpha_folder_parth = main_path_p + '/decimated_dn_'+rftn_target
if not os.path.exists(alpha_folder_parth):
    os.makedirs(alpha_folder_parth) 

# loop over folders
for folder in folders:
    if folder[0] == '.':
        continue
    files_in_folder = os.listdir(main_path + '/' + folder)
    alpha_folder_parth_folder = os.path.join(alpha_folder_parth, folder)
    if not os.path.exists(alpha_folder_parth_folder):
        os.makedirs(alpha_folder_parth_folder)
    

    
    for file in files_in_folder:
            if '.SAC' in file:
                file_path = main_path + '/' + folder + '/' + file
                subprocess.call(['cp', file_path, alpha_folder_parth_folder])
    # create a new folder for the rotated files, plus GOOD folder
    if not os.path.exists(main_path + '/' + folder + '/GOOD'):
        os.makedirs(main_path + '/' + folder + '/GOOD')
    print(folder)
    # skip file that starts with '.'
    if folder[0] == '.':
        continue
    # list all the files in the folder
    files = os.listdir(rotated_files + '/' + folder)
    # loop over files
    for file in files:
        #radial_file ends with .r
        if file[-2:] == '.r':
            radial_file = file
            # path to radial file
            radial_path = rotated_files + '/' + folder + '/' + radial_file
            print(radial_path)
            subprocess.call(['cp', radial_path, main_path + '/' + folder + '/GOOD'])
            # copy the file to main_path+folder
            subprocess.call(['cp', radial_path, main_path + '/' + folder])
            subprocess.call(['cp', radial_path, alpha_folder_parth_folder])

        elif file[-2:] == '.t':
            transverse_file = file
            # path to transverse
            transverse_path = rotated_files + '/' + folder + '/' + transverse_file
            print(transverse_path)
            subprocess.call(['cp', transverse_path, main_path + '/' + folder + '/GOOD'])
            # copy the file to main_path+folder
            subprocess.call(['cp', transverse_path, main_path + '/' + folder])
            subprocess.call(['cp', transverse_path, alpha_folder_parth_folder])

        elif file[-2:] == '.z':
            vertical_file = file
            # path to vertical
            vertical_path = rotated_files + '/' + folder + '/' + vertical_file
            print(vertical_path)
            subprocess.call(['cp', vertical_path, main_path + '/' + folder + '/GOOD'])
            

            # read the file in final destination with obspy
            #st = obspy.read(vertical_path)
            # get the time series
            #tr = st[0]
            # Multiply by -1 to invert the polarity
            #tr.data = tr.data * 1
            # write the file
            #tr.write(main_path + '/' + folder + '/GOOD/' + vertical_file, format='SAC')
            # copy the file to main_path+folder
            subprocess.call(['cp', main_path + '/' + folder + '/GOOD/' + vertical_file, main_path + '/' + folder])
            subprocess.call(['cp', main_path + '/' + folder + '/GOOD/' + vertical_file, alpha_folder_parth_folder])
        else:
            continue

    # run cut script with event folder name as input
    # how to run cut script = DOCUT1 event_folder_name
    subprocess.call([os.path.join(main_path,cut_name), folder], cwd=main_path)

    # run decon script with event folder name as input
    # how to run decon script = DODECON event_folder_name
    subprocess.call([os.path.join(main_path,decon_name), folder], cwd=main_path)

    # decon folder path
    decon_path = main_path + '/' + folder + '/' + decon_folder

    # list all the files in the decon folder
    decon_files = os.listdir(decon_path)
    print(decon_files)

    # loop over files in decon folder
    for decon_file in decon_files:
        # skip file that starts with '.'
        if decon_file[0] == '.':
            continue
        file_split = decon_file.split('_')
        networ = decon_file[0:2]
        #station = decon_file[3:6]
        station_name = file_split[1]
        if len(station_name) == 3:
            station = station_name
            alpha = decon_file[7:10]
            rftn = decon_file[13:16]
            component = decon_file[17:18]
        elif len(station_name) == 4:
            station = station_name
            alpha = decon_file[8:11]
            rftn = decon_file[14:17]
            component = decon_file[18:19]

        if rftn == target_alpha:

            # create new file name with the following format: NET_STA_ALPHA.i.eq{rftn}.{component}
            funclab_format = networ + '_' + station + '_' + alpha + '.i.eq'  + component
            print(funclab_format)
            # path to the new file
            funclab_format_path = main_path + '/' + folder + '/' + funclab_format
            print(funclab_format_path)
            alpha_folder_parth_folder = alpha_folder_parth + '/' + folder  + '/' + funclab_format
            print(funclab_format_path)

            decon_file_path = decon_path + '/' + decon_file
            print(decon_file_path)

            # write the file to the decon folder
            # subprocess.call(['cp', decon_path + '/' + decon_file, funclab_format_path])
            # subprocess.call(['cp', decon_path + '/' + decon_file, alpha_folder_parth_folder])
            shutil.copy(decon_path + '/' + decon_file, funclab_format_path)
            shutil.copy(decon_path + '/' + decon_file, alpha_folder_parth_folder) 
            # # copy the file to main_path+folder
            # subprocess.call(['cp', decon_file_path, funclab_format_path])
            # subprocess.call(['cp', decon_file_path, alpha_folder_parth_folder])
            # # mv the file to the main folder
            # subprocess.call(['mv', decon_path + '/' + decon_file, main_path + '/' + folder])
            #subprocess.call(['mv', decon_path + '/' + decon_file, alpha_folder_parth_folder])
            # # read the file with obspy
            # st = obspy.read(funclab_format_path)
            # # get the time series
            # tr = st[0]

            # # assign B and E time
            # tr.stats.sac.b = -5
            # tr.stats.sac.e = 55

            # # read user1 and user2
            # user4 = tr.stats.sac.user4
            # tr.stats.sac.user1 = user4
            # tr.stats.sac.leven = True
            # tr.stats.sac.delta = 0.1

            # # select and slice data between B and E time (in seconds) use start = B and end = E
            # #tr = tr.slice(starttime=tr.stats.sac.b, endtime=tr.stats.sac.e)
            
            # #tr = tr.slice(tr.stats.sac.b, tr.stats.sac.e)
            # # tr.trim(tr.stats.sac.b, tr.stats.sac.e)
            # #slice the data between certain points 
            # #tr = tr.slice(0, 60)
            # # + tr.stats.sac.b, tr.startTime + tr.stats.sac.e)



            # # write the file
            # tr.write(funclab_format_path, format='SAC')


            # # copy the new_file_path to one level up
            # subprocess.call(['cp', funclab_format_path, main_path + '/' + folder+ '/' +funclab_format])




