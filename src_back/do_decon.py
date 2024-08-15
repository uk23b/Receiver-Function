import os
import shutil
import subprocess

main_folder = '/Volumes/UNTITLE/decimated_dn_1.0_rotated/'

# cut script
cut_name = 'DOCUT1'

# decon script
decon_name = 'DODECON'


for event_folder in os.listdir(main_folder):
    event_path = os.path.join(main_folder, event_folder)
    # if event path is a directory
    if os.path.isdir(event_path):
        # run DODECON
        subprocess.call(['./' + decon_name, event_folder], cwd=main_folder)