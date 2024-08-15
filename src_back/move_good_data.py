import os
import shutil
import obspy

# Define the main path that contains all the receiver function files
main_path = '/Volumes/UNTITLE/decimated_dn_2.5/'
final_path = '/Volumes/UNTITLE/decimated_dn_2.5_GOOD/'

# Define the threshold value for user 5 header
threshold = 80

# Create a dictionary to store station information
station_info = {}

# Iterate through all subdirectories under the main path
for root, dirs, files in os.walk(main_path):
    for filename in files:
        if filename.endswith(".eqr"):
            eqr_path = os.path.join(root, filename)
            try:
                # Use ObsPy to read the SAC header values
                st = obspy.read(eqr_path)
                user5_value = st[0].stats.sac.user5
                print(user5_value)
                
                # Check if user 5 value is above the threshold
                if user5_value > threshold:
                    # Extract station name from the eqr filename
                    station_name = filename.split(".")[0]
                    
                    # Create a new directory structure in a different location
                    new_path = os.path.join(final_path, station_name)
                    print(new_path)
                    
                    # Create directories if they don't exist
                    os.makedirs(new_path, exist_ok=True)
                    
                    # Move all files (eqr, eqt, i.r, i.t, i.z) to the new directory
                    for ext in ["eqr", "eqt", "i.r", "i.t", "i.z"]:
                        src_file = os.path.join(root, filename.replace(".eqr", "." + ext))
                        dest_file = os.path.join(new_path, filename.replace(".eqr", "." + ext))
                        print(src_file, dest_file)
                        shutil.move(src_file, dest_file)
                    
                    print(f"Moved files from {root} to {new_path}")
                    
                    # Store station information for later moving of core SAC files
                    station_info[station_name] = new_path
                        
            except Exception as e:
                print(f"Error processing {eqr_path}: {e}")

# Now, move the related core SAC files
for station_name, new_path in station_info.items():
    for core_ext in ["HHE", "HHN", "HHZ"]:
        core_file = f"{station_name}.{core_ext}..M.*.SAC"
        core_files = [f for f in os.listdir(main_path) if f.startswith(core_file)]
        for core_file in core_files:
            src_core_file = os.path.join(main_path, core_file)
            dest_core_file = os.path.join(new_path, core_file)
            print(src_core_file, dest_core_file)
            shutil.move(src_core_file, dest_core_file)
