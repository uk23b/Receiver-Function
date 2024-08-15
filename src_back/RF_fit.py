import os
import obspy
import shutil

rftn = '2.5'
gauss = '2.5'

target_freq = 10

# Output file
out_file = 'output_fit.txt'

# Main path that contains all the raw data.
main_folder = '/Volumes/UNTITLE/18_final_products/final10/RAWDATA/'
main_path = '/Volumes/UNTITLE/18_final_products/final10/RAWDATA/decimated_dn_1.0/'

f = open(main_path + '/' + out_file, 'w')

# List folders
folders = os.listdir(main_path)

# List only folders in the main path
folders = [folder for folder in folders if os.path.isdir(os.path.join(main_path, folder))]

# Sort folders
folders.sort()

# Create an output folder if not exist
if not os.path.exists(main_folder + 'GOOD_DATA'):
    os.makedirs(main_folder + 'GOOD_DATA')

# Loop over folders
for folder in folders:
    print(folder)
    
    # Skip folders that start with '.'
    if folder[0] == '.':
        continue
    
    # Create a directory in the GOOD_DATA folder for the current folder's data
    good_data_folder = os.path.join(main_folder, 'GOOD_DATA', folder)
    if not os.path.exists(good_data_folder):
        os.makedirs(good_data_folder)
    
    # List all the files in the folder
    files = os.listdir(os.path.join(main_path, folder))
    
    # Read sac files ending with .eqr
    files_eqr = [file for file in files if file.endswith('.eqr')]
    
    # Loop over .eqr files
    for eqr_file in files_eqr:
        # Read sac file
        st = obspy.read(os.path.join(main_path, folder, eqr_file))
        
        # Read user5 header
        user5 = st[0].stats.sac.user5
        user5 = float(user5)
        
        networ = st[0].stats.sac.knetwk
        station = st[0].stats.sac.kstnm
        
        # Print information
        print(f"File: {eqr_file}")
        print(f"User5: {user5}")
        
        # Check if user5 is greater than 80 (or any other condition)
        if user5 > 90:
            print('good')
            # Write to the output file, file name and user5 value, followed by a new line

            f.write(f"{eqr_file} {user5}\n")
            
            # Loop over all files in the folder
            for file in files:
                # Check if the file has the same station name as the .eqr file
                if station in file:
                    source_path = os.path.join(main_path, folder, file)
                    destination_path = os.path.join(good_data_folder, file)
                    
                    if os.path.isfile(source_path):
                        shutil.copy2(source_path, destination_path)

# Close the output file
f.close()
