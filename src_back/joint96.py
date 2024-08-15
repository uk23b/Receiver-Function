# joint inversion of receiver function and surface wave dispersion data
# import modules
import os, sys
import numpy as np
import subprocess
import pandas as pd
import matplotlib.pyplot as plt

joint96 = 'joint96'
infile = './DOIT.deep'
infile_2 = './DOIT.deep_2'

# main working directory
main_path = '/Volumes/LaCie2/17_Hermann/test32/JOINT/'
# work folder
work_folder = 'work_joint'

# change current working directory to main_path+work_folder
os.chdir(main_path + work_folder)

# main path that contains all the receiver function files
main_path_rec = '/Volumes/LaCie2/17_Hermann/test32/JOINT/data/CCP_RFs/'

# list of receiver function files
rec_files = os.listdir(main_path_rec)
print(rec_files)

# create a 'work_joint' directory if not exists
if not os.path.exists(main_path + work_folder):
    os.makedirs(main_path + work_folder)

print('work folder created')
print(main_path)
print(main_path + work_folder)

#out file
out_file = 'joint.out'
info_out = 'joint_info.out'

#######
# first line of jobs.d file
line1 = '  0.00499999989  0.00499999989  0.  0.00499999989  0.'
line2 = '    1    0    0    0    1    1    1    0    1    0'
line3 = 'start.mod'
#line3 = 'model.m'
line5 = 'rftn.lst'

# joint96 parameters #
cleanup = '39'
RFTN = '0' # 2x RFTN computation
damping = '5.'
weigth_RF_SW = '0.5'
dif_smoothing = '1'
time_start = '-2'
time_end = '10'

num_iter = '1'

# sort rec_files by longitude
rec_files.sort(key=lambda x: float(x.split('_')[1]))

# loop over receiver function files (range(len(rec_files)) to loop over all files)
for i in range(len(rec_files)):
    # create a rftn.lst file that contains the list of receiver function files (delete the file if exists)
    if os.path.exists(main_path + work_folder + '/rftn.lst'):
        os.remove(main_path + work_folder + '/rftn.lst')

    # create a rftn.lst file that contains the list of receiver function files
    f = open(main_path + work_folder + '/rftn.lst', 'w')
    # skip file that starts with '.'
    if rec_files[i][0] == '.': 
        continue
    print(rec_files[i])
    rec_file_path = main_path_rec + rec_files[i]
    print(rec_file_path)
    print(f)

    # get latitude and longitude from the file name
    # split file name by '.'
    file_split = rec_files[i].split('_')
    print(file_split)
    longitude = file_split[1]
    # remove .sac from the end of the file name in file_split[2]
    latitude = file_split[2].split('.')[0] + '.' + file_split[2].split('.')[1]
    print(longitude, latitude)

    out_file = 'modl.out'
    info_out = 'info.out' 

    # update the out_file and info_out file names with format: modl_#_#.out and info_#_#.out longitude and latitude

    
    out_file = out_file.split('.')[0] + '_' + longitude + '_' + latitude + '.' + 'out'
    info_out = info_out.split('.')[0] + '_' + longitude + '_' + latitude + '.' + 'out'
    print(out_file, info_out)

    # write name of the file to output file
    f.write(rec_file_path + '\n')
    f.close()

    # create a jobs.d file 
    f2 = open(main_path + work_folder + '/jobs.d', 'w')
    # write first line
    f2.write(line1 + '\n')
    # write second line
    f2.write(line2 + '\n')
    # write third line
    f2.write(line3 + '\n')

    # make folder for each node
    node_folder = 'node_' + longitude + '_' + latitude
    if not os.path.exists(main_path + work_folder + '/' + node_folder):
        os.makedirs(main_path + work_folder + '/' + node_folder)

    # fourth line is dispersion file name
    # get name of dispersion file from /data/Disp_Curves/ folder
    # dispersion file format is 'pv.longitude_latitude'
    disp_file = 'pv.' + longitude + '_' + latitude
    disp_file_path = main_path + 'data/Disp_Curves/' + disp_file
    f2.write(disp_file_path + '\n')
    # write fifth line
    f2.write(line5 + '\n')
    f2.close()

    # create info.out file based on longitude and latitude(with format)
    modl_out_file = 'modl.' + longitude + '_' + latitude + '.out'
    info_out_file = 'info.' + longitude + '_' + latitude + '.txt'
    jt_out_file = 'jnt.' + longitude + '_' + latitude + '.txt'

    # create a inv.info file
    f3 = open(main_path + work_folder +  info_out_file, 'w')

    f5 = open(main_path + work_folder +  jt_out_file, 'w')

    f6 = open(main_path + work_folder +  modl_out_file, 'w')

        # #rftn96 39
    subprocess.call(infile, stdout=f5)
    #subprocess.call(infile_2, stdout=f5)
    
    subprocess.call([joint96, cleanup], stdout=f5)
    subprocess.call([joint96, '32' ,damping], stdout=f5)
    subprocess.call([joint96, '36' ,dif_smoothing], stdout=f5)
    subprocess.call([joint96, '33' ,time_start, '34', time_end], stdout=f5)
    
    subprocess.call([joint96, '1'], stdout=f5)
    subprocess.call([joint96, '2'], stdout=f5)
    subprocess.call([joint96, '6'], stdout=f5)

    

    # subprocess.call([joint96, '1'], stdout=f5)
    # subprocess.call([joint96, '2'], stdout=f5)
    # subprocess.call([joint96, '6'], stdout=f5)



    subprocess.call(['srfphr96'])
    command1 = 'mv SRFPHR96.PLT {}_{}_rffit.plt'.format(longitude, latitude)
    subprocess.call([command1], shell=True)
    command2 = 'plotnps -EPS -K < {}_{}_rffit.plt > {}_{}_rffit.eps'.format(longitude, latitude, longitude, latitude)
    subprocess.call([command2], shell=True)
    command3 = 'convert -trim {}_{}_rffit.eps {}_{}_rffit.png'.format(longitude, latitude, longitude, latitude)
    subprocess.call([command3], shell=True)

    subprocess.call(['rftnpv96'])
    #plotnps -EPS -K -F7 -W10 < RFTNPV96.PLT > figrfn1.eps
    command4 = 'plotnps -EPS -K -F7 -W10 < RFTNPV96.PLT > {}_{}_rfn1.eps'.format(longitude, latitude)
    subprocess.call([command4], shell=True)
    command5 = 'convert -trim {}_{}_rfn1.eps {}_{}_rfn1.png'.format(longitude, latitude, longitude, latitude)
    subprocess.call([command5], shell=True)
    # shwmod96 -K 1 -W 0.05 model.true
    command6 = 'shwmod96 -K 1 -W 0.05 model.true'
    #mv SHWMOD96.PLT T.PLT
    command7 = 'mv SHWMOD96.PLT T.PLT'
    command8 = 'shwmod96 -K -1 tmpmod96.???'
    command9 = 'mv SHWMOD96.PLT T1.PLT'
    command10 = 'cat T.PLT T1.PLT > IT.PLT'
    # plotnps -EPS -K -F7 -W10 < IT.PLT > figrfn2.eps
    command11 = 'plotnps -EPS -K -F7 -W10 < IT.PLT > {}_{}_rfn2.eps'.format(longitude, latitude)
    command12 = 'convert -trim {}_{}_rfn2.eps {}_{}_rfn2.png'.format(longitude, latitude, longitude, latitude)
    subprocess.call([command6], shell=True)
    subprocess.call([command7], shell=True)
    subprocess.call([command8], shell=True)
    subprocess.call([command9], shell=True)
    subprocess.call([command10], shell=True)
    subprocess.call([command11], shell=True)
    subprocess.call([command12], shell=True)

    subprocess.call([joint96, '18'], stdout=f5)
    #subprocess.call([joint96, '28'], stdout=f5)
    subprocess.call(['joint96', '28'], stdout=f5)
    # subprocess.call(['joint96', '45'], stdout=f5)
    # subprocess.call(['joint96', '47'], stdout=f5)

    # # close files
    # f5.close()
    # f6.close()
    


    # move files to node folder

    command13 = 'mv {}_{}_rffit.plt {}'.format(longitude, latitude, node_folder)
    command14 = 'mv {}_{}_rffit.eps {}'.format(longitude, latitude, node_folder)
    command15 = 'mv {}_{}_rffit.png {}'.format(longitude, latitude, node_folder)
    command16 = 'mv {}_{}_rfn1.eps {}'.format(longitude, latitude, node_folder)
    command17 = 'mv {}_{}_rfn1.png {}'.format(longitude, latitude, node_folder)
    command18 = 'mv {}_{}_rfn2.eps {}'.format(longitude, latitude, node_folder)
    command19 = 'mv {}_{}_rfn2.png {}'.format(longitude, latitude, node_folder)
    subprocess.call([command13], shell=True)
    subprocess.call([command14], shell=True)
    subprocess.call([command15], shell=True)
    subprocess.call([command16], shell=True)
    subprocess.call([command17], shell=True)
    subprocess.call([command18], shell=True)
    subprocess.call([command19], shell=True)

    subprocess.call([joint96, '18'], stdout=f5)
    f5.close()
