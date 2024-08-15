import os
import shutil

main_folder = '/Volumes/UNTITLE/decimated_dn_1.0_rotated/'

for event_folder in os.listdir(main_folder):
    event_path = os.path.join(main_folder, event_folder)
    if os.path.isdir(event_path):
        good_folder = os.path.join(event_path, 'GOOD')
        os.makedirs(good_folder, exist_ok=True)
        for root, _, files in os.walk(event_path):
            for file in files:
                if file.endswith(('.r', '.t', '.z')):
                    file_path = os.path.join(root, file)
                    destination_path = os.path.join(good_folder, file)
                    if not os.path.exists(destination_path):
                        shutil.move(file_path, destination_path)