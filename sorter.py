import os
import shutil
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()

# Create an ArgumentParser to handle command-line arguments
parser.add_argument('--o', dest='path', required=True, help='Path to the directory containing files to be sorted.')
parser.add_argument('--d', dest='datetimeStr', required=True, help='Datetime folder name.')

# Parse the command-line arguments
args = parser.parse_args()

output_folder = args.path
datetime_str = args.datetimeStr

# Create the "SORTED" subfolder if it doesn't exist
# sorted_folder = os.path.join(directory, "SORTED")
# os.makedirs(sorted_folder, exist_ok=True)

# Get the current date and time
# current_datetime = datetime.now()
# datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create the subfolder for the date-time if it doesn't exist
datetime_folder = os.path.join(output_folder, datetime_str)
os.makedirs(datetime_folder, exist_ok=True)

# Get a list of all files in the directory
files = os.listdir(output_folder)

# Initialize counters for file renaming
counters = {}

# Loop through each file in the directory
for file in files:
    # Skip the "datetime_str" result folder itself and files without extensions
    if file == datetime_str or not os.path.splitext(file)[1]:
        continue

    # Split the filename into name and extension
    name, ext = os.path.splitext(file)

    # Get the current counter value for that extension
    current_counter = counters.get(ext, 0) + 1

    # Update the counter for that extension
    counters[ext] = current_counter

    if ext == '.mp3':
        new_name = 'voiceover.mp3'
    else:
        # Create the new name using the counter and extension
        new_name = str(current_counter).zfill(3) + ext

    # Build the old and new paths
    old_path = os.path.join(output_folder, file)
    new_path = os.path.join(datetime_folder, new_name)
    print(old_path, new_path)

    # Move the file to the "/datetime_folder" subfolder with the new name
    shutil.move(old_path, new_path)
