# RF data is a time series data, in this script, we will classify RF data.

# Input: Z, N, E component data (number of inputs: 3):  
# Output: RF data (number of outputs: 1): if output is good, then it is 1, otherwise it is 0.

# we will classify based on output quality. If the output quality is good then input RF data is good, otherwise it is bad.

import os, sys

script_name = sys.argv[0] # source file path, sys.argv[0] is the script name, sys.argv[1] is the source file path
print("Source path: " + script_name)
source_path = '/Volumes/UNTITLE/14_File_Format_Conversion_FUNCLAB'

print("Source path: " + source_path)

# list all files in the source_path
Input_RF_files = os.listdir(source_path)
print("Input RF files: " + str(Input_RF_files))

Input_folder = "Output_2016_2017_2018_2019"
# join the directory of the script and the input folder
Input_path = os.path.join(source_path, Input_folder)
print("Input path: " + Input_path)

# list all files in the Input_path
Input_RF_files = os.listdir(Input_path)
print("Input RF files: " + str(Input_RF_files))



