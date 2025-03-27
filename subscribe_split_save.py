import subprocess
import os
import random
import argparse
import json
import time

# Argument parsing
parser = argparse.ArgumentParser(description="Create slideshow with overlay.")
parser.add_argument('--i', dest='input_dir', required=True, help='Path to the directory containing input files')
parser.add_argument('--n', type=str, default='Model Name', dest='model_name', help='Model name.')
parser.add_argument('--f', type=int, default=90, dest='fontsize', help='Font size')

args = parser.parse_args()

# Start timing the entire process
start_time = time.time()

input_dir = args.input_dir
input_video = os.path.join(input_dir, 'slideshow_with_audio.mp4')
overlay_video = 'TEMPLATE/name_subscribe_like.mp4'
model_name = args.model_name.strip('"')
output_video = os.path.join(input_dir, f"{model_name.replace(' ', '_')}.mp4")
chromakey_color = '65db41'
delay = 21  # Start time for the overlay (in seconds)
fontcolor = random.choice(['FF00B4', 'ff6600', '0b4178'])
fontsize = args.fontsize

# Temporary file paths
first_part = os.path.join(input_dir, "first_part.mp4")
edited_first_part = os.path.join(input_dir, "edited_first_part.mp4")
second_part = os.path.join(input_dir, "second_part.mp4")
concat_file = os.path.join(input_dir, "concat_list.txt")

# Split the video into two parts: first 45 seconds and the rest
split_command = [
    'ffmpeg', '-loglevel', 'error', 
    '-i', input_video,
    '-t', '60', '-c', 'copy', first_part,  # First 60 seconds
    '-ss', '60', '-c', 'copy', second_part  # Remaining video
]
# subprocess.run(split_command)


# Start timing the entire process
start_time = time.time()

# Step 1: Split the Input Video
print("Step 1: Splitting the input video...")
step_start = time.time()


# Step 1: Cut the first part (roughly, using 60 seconds)
split_command_1 = [
    'ffmpeg',  '-y', '-loglevel', 'error', '-i', input_video, '-t', '60', '-c', 'copy', first_part
]
subprocess.run(split_command_1, check=True)


# Step 2: Analyze the first part to find the last keyframe

probe_command = [
    'ffprobe', '-select_streams', 'v:0', '-show_frames', '-show_entries',
    'frame=key_frame,pts_time,pkt_dts_time,duration_time', '-of', 'json', first_part
]
probe_result = subprocess.run(probe_command, capture_output=True, text=True, check=True)
frames = json.loads(probe_result.stdout)['frames']

# Extract the last keyframe timestamp
frame_before_last_keyframe_time = None
for frame in frames:
    if frame['key_frame'] == 1 and 'pts_time' in frame:
        last_keyframe_time = float(frame['pts_time'])
        frame_before_last_keyframe_time = last_keyframe_time - float(frame['duration_time'])


if frame_before_last_keyframe_time is None:
    raise ValueError("No keyframes found in the first part!")

print(f"Last keyframe time in first part: {last_keyframe_time} seconds")

# Command to extract the first part up to the keyframe
split_first_part_command = [
    'ffmpeg', '-y', '-loglevel', 'error',
    '-i', input_video,
    '-to', f"{last_keyframe_time}",  # Cut up to the last keyframe
    '-c:v', 'libx264', '-preset', 'fast',  # Re-encode for smooth playback
    '-c:a', 'aac', first_part
]
subprocess.run(split_first_part_command, check=True)
print(f"Step 1 completed in {time.time() - step_start:.2f} seconds.")

# Command to extract the second part starting from the keyframe
split_second_part_command = [
    'ffmpeg', '-y', '-loglevel', 'error',
    '-ss', f"{last_keyframe_time}",  # Start from the last keyframe
    '-i', input_video,
    '-c:v', 'libx264', '-preset', 'fast',  # Re-encode to align streams
    '-c:a', 'aac', second_part
]
subprocess.run(split_second_part_command, check=True)
print(f"Step 2 completed in {time.time() - step_start:.2f} seconds.")

print("Videos split successfully!")

# Step 3: Overlay the Videos
print("Step 3: Overlaying videos...")
step_start = time.time()

# Apply overlay and chromakey to the first part
overlay_command = [
    'ffmpeg',
    '-loglevel', 'error',
    '-i', first_part,
    '-i', overlay_video,
    '-filter_complex', f"[1:a]adelay={delay*1000}|{delay*1000},volume=0.5[a1];[0:a]volume=1.0[a0];[a0][a1]amix=inputs=2:normalize=0[aout];[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS+{delay}/TB,chromakey=color=0x{chromakey_color}:similarity=0.18:blend=0.0[ckout];[v0][ckout]overlay=enable='between(t\,{delay},{delay+23})',drawtext=text='{model_name}':x=((w-tw)/2+110):y=((h/2)-35):enable='between(t\,22,27)':fontfile=/Users/a/Library/Fonts/Montserrat-SemiBold.otf:fontsize={fontsize}:fontcolor=0x{fontcolor}:shadowcolor=black:shadowx=4:shadowy=2:alpha=0.8[out]",
    '-map', '[out]', '-map', '[aout]',
    '-c:v', 'libx264', '-c:a', 'aac', '-y', edited_first_part
]
subprocess.run(overlay_command)

print(f"Step 3 completed in {time.time() - step_start:.2f} seconds.")
print("Step 4: Concatenating videos...")
step_start = time.time()

# Create a concat list for joining the videos
with open(concat_file, 'w') as file:
    file.write(f"file '{edited_first_part}'\n")
    file.write(f"file '{second_part}'\n")

# Concatenate the processed first part with the untouched second part
concat_command = [
    'ffmpeg',  '-y', '-f', 'concat', '-safe', '0',
    '-i', concat_file, '-c', 'copy', output_video
]
subprocess.run(concat_command)

print(f"Step 4 completed in {time.time() - step_start:.2f} seconds.")

# Cleanup temporary files
# os.remove(first_part)
# os.remove(edited_first_part)
# os.remove(second_part)
# os.remove(concat_file)

print(f"Finished processing. Output video: {output_video}")
