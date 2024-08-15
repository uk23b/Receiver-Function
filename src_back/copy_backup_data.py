import os
import shutil

main_source_path = '/Volumes/LaCie1/from_UNTITLED_main/14_File_Format_Conversion_FUNCLAB/decimated_dn_2.5/'
main_dest_path = '/Volumes/UNTITLE/decimated_dn_2.5'

# Walk through the source directory and its subdirectories
for root, _, files in os.walk(main_source_path):
    for file in files:
        source_file = os.path.join(root, file)
        
        # Get the relative path from main_source_path (excluding the source filename)
        relative_path = os.path.relpath(os.path.dirname(source_file), main_source_path)
        
        # Construct the corresponding destination directory path under main_dest_path
        dest_dir = os.path.join(main_dest_path, relative_path)
        
        # Construct the destination file path
        dest_file = os.path.join(dest_dir, file)
        
        # Check if the file already exists in the destination directory
        if not os.path.exists(dest_file):
            # Create the directory structure in the destination path if it doesn't exist
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy the file from source to destination
            shutil.copy2(source_file, dest_file)
            print(f"Copied: {source_file} -> {dest_file}")
        else:
            print(f"Skipped (already exists): {source_file} -> {dest_file}")
