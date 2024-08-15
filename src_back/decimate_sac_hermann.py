import obspy
import os
import glob
from tqdm import tqdm

target_sampling_rate = 10

# Path to sac files
main_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/Output_test/'
output_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB/'

# List of folders
folders = os.listdir(main_path)
print(folders)

for folder in tqdm(folders, desc='Processing folders'):
    folder_path = os.path.join(main_path, folder)
    
    # List of sac files
    files = glob.glob(folder_path + '/*.SAC')
    
    for file in tqdm(files, desc='Processing files'):
        # Read sac file
        st = obspy.read(file)
        
        # Sampling rate
        print(st[0].stats.sampling_rate)
        
        if st[0].stats.sampling_rate == 200:
            st.decimate(2)

        dec_rate = st[0].stats.sampling_rate / target_sampling_rate
        print(dec_rate)
        dec_rate = int(dec_rate)
        
        # Decimate
        st.decimate(dec_rate)
        print(st[0].stats.sampling_rate)
        
        # Create an output folder for each event if it doesn't exist
        output_folder = os.path.join(output_path, 'decimated', folder)
        os.makedirs(output_folder, exist_ok=True)
        
        # Write sac file
        output_file = os.path.join(output_folder, os.path.basename(file))
        st.write(output_file, format='SAC')
        
print('Done')
