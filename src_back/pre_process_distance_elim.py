import obspy
import os, sys
import glob

# main path event folders that contains sac files for each component
main_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/decimated/'
# list of folders
folders = os.listdir(main_path)
#print(folders)
for folder in folders:
    # path to event folder
    folder_path = os.path.join(main_path, folder)
    # list of sac files
    files = glob.glob(folder_path + '/*.SAC')
    #print(files)
    for file in files:
    # read sac file
        st = obspy.read(file)
        print(st)

        # Check if 'dist' exists in sac.stats.sac dictionary
        if 'dist' not in st[0].stats.sac:
            continue
        else:
            dist = st[0].stats.sac.dist
            gcarc = st[0].stats.sac.gcarc

        print(gcarc)

        # if gcarc is bigger than 90 degree or smaller than 20 degree,
        # move the file to another folder that has the same name as the event folder under LDIST folder
        if gcarc > 90 or gcarc < 20:
            # create a folder under LDIST folder if it does not exist
            if not os.path.exists(main_path + '/LDIST' + '/' + folder):
                os.makedirs(main_path + '/LDIST' + '/' + folder)
                print('Folder created:', folder_path + '/LDIST' + '/' + folder)
            # move the file to the folder
            os.rename(file, main_path + '/LDIST' + '/' + folder + '/' + os.path.basename(file))
            print('File moved:', file)



