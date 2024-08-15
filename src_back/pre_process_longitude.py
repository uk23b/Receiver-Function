import obspy
import os
import glob
import shutil

# main path event folders that contain SAC files for each component
main_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/decimated/'

# list of folders
folders = os.listdir(main_path)

for folder in folders:
    # path to event folder
    folder_path = os.path.join(main_path, folder)
    
    # list of SAC files
    files = glob.glob(folder_path + '/*.SAC')

    for file in files:
        try:
            # read SAC file
            st = obspy.read(file)
            print(st)
            
            # station longitude and latitude
            stla = st[0].stats.sac.stla
            stlo = st[0].stats.sac.stlo

            # if station longitude is smaller than 36, move the file to the 'LONGROUP' folder under the event folder
            if stlo < 36:
                longroup_folder = os.path.join(main_path, 'LONGROUP', folder)
                if not os.path.exists(longroup_folder):
                    os.makedirs(longroup_folder)
                    print('Folder created:', longroup_folder)
                
                # move the file to the 'LONGROUP' folder
                new_file_path = os.path.join(longroup_folder, os.path.basename(file))
                shutil.move(file, new_file_path)
                print('File moved:', new_file_path)
        
        except KeyError as e:
            print("KeyError: 'stlo'. Moving file to 'Nolon' folder.")
            nolon_folder = os.path.join(main_path, 'Nolon', folder)
            if not os.path.exists(nolon_folder):
                os.makedirs(nolon_folder)
                print('Folder created:', nolon_folder)
            
            # move the file to the 'Nolon' folder
            new_file_path = os.path.join(nolon_folder, os.path.basename(file))
            shutil.move(file, new_file_path)
            print('File moved:', new_file_path)
