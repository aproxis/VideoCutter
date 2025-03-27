import subprocess
import os
import random
import argparse
import time

# Start timing the entire process
start_time = time.time()

# Argument parsing
parser = argparse.ArgumentParser(description="Create slideshow with overlay.")
parser.add_argument('--i', dest='input_dir', required=True, help='Path to the directory containing input files')
parser.add_argument('--n', type=str, default='Model Name', dest='model_name', help='Model name.')
parser.add_argument('--f', type=int, default=90, dest='fontsize', help='Font size')
parser.add_argument('--o', type=str, default='vertical', dest='orientation', help='Orientation (vertical or horizontal).')

args = parser.parse_args()


video_orientation = args.orientation
input_dir = args.input_dir
input_video = os.path.join(input_dir, 'slideshow_with_audio.mp4')

if video_orientation == 'vertical':
    overlay_video = 'TEMPLATE/name_subscribe_like.mp4'
else:
    overlay_video = 'TEMPLATE/name_subscribe_like_horizontal.mp4'

model_name = args.model_name.strip('"')
output_video = os.path.join(input_dir, f"{model_name.replace(' ', '_')}.mp4")
chromakey_color = '65db41'
delay = 21  # Start time for the overlay (in seconds)
fontcolor = random.choice(['FF00B4', 'ff6600', '0b4178'])
fontsize = args.fontsize

print("Overlaying videos...")
step_start = time.time()

# Apply overlay and chromakey to the first part
overlay_command = [
    'ffmpeg',
    '-loglevel', 'error',
    '-i', input_video,
    '-i', overlay_video,
    '-filter_complex', f"[1:a]adelay={delay*1000}|{delay*1000},volume=0.5[a1];[0:a]volume=1.0[a0];[a0][a1]amix=inputs=2:normalize=0[aout];[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS+{delay}/TB,chromakey=color=0x{chromakey_color}:similarity=0.18:blend=0.0[ckout];[v0][ckout]overlay=enable='between(t\,{delay},{delay+23})',drawtext=text='{model_name}':x=((w-tw)/2+110):y=((h/2)-35):enable='between(t\,22,27)':fontfile=/Users/a/Library/Fonts/Montserrat-SemiBold.otf:fontsize={fontsize}:fontcolor=0x{fontcolor}:shadowcolor=black:shadowx=4:shadowy=2:alpha=0.8[out]",
    '-map', '[out]', '-map', '[aout]',
    '-c:v', 'libx264', '-c:a', 'aac', '-y', output_video
]
subprocess.run(overlay_command)

print(f"Name + Subscribe: {time.time() - step_start:.2f} seconds.")

print(f"Finished processing. Output video: {output_video}")
