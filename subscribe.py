import subprocess
import os
import random
import argparse
import time
import json

# Start timing the entire process
start_time = time.time()

# Argument parsing
parser = argparse.ArgumentParser(description="Create slideshow with overlay.")

parser.add_argument('--i', dest='input_dir', required=True, help='Path to the directory containing input files')
parser.add_argument('--tpl', type=str, default='TEMPLATE', dest='template_folder', help='Template folder')


parser.add_argument('--t', type=str, default='Model Name', dest='title', help='Video title')
parser.add_argument('--tf', type=str, default='Montserrat-SemiBold.otf', dest='title_fontfile', help='Font file for title text')
parser.add_argument('--tfs', type=int, default=90, dest='title_fontsize', help='Title font size')
parser.add_argument('--tfc', type=str, default='random', dest='title_fontcolor', help='Font color (hex code without #, or "random")')
parser.add_argument('--osd', type=int, default=21, dest='start_delay', help='Delay before overlay appears (in seconds)')
parser.add_argument('--tad', type=int, default=1, dest='title_appearance_delay', help='Delay before title appears (in seconds)')
parser.add_argument('--tvt', type=int, default=5, dest='title_visible_time', help='Duration title remains visible (in seconds)')
parser.add_argument('--tyo', type=int, default=-35, dest='title_y_offset', help='Title y offset')
parser.add_argument('--txo', type=int, default=110, dest='title_x_offset', help='Title x offset')



parser.add_argument('--chr', type=str, default='65db41', dest='chromakey_color', help='Chromakey color (hex code without #)')
parser.add_argument('--cs', type=float, default=0.18, dest='chromakey_similarity', help='Chromakey similarity (0-1)')
parser.add_argument('--cb', type=float, default=0, dest='chromakey_blend', help='Chromakey blend (0-1)')

parser.add_argument('--srt', type=str, default='0', dest='generate_srt', help='Add SRT subtitles? 0/1')

parser.add_argument('--o', type=str, default='vertical', dest='orientation', help='Orientation (vertical or horizontal).')

args = parser.parse_args()

video_orientation = args.orientation
input_dir = args.input_dir
input_video = os.path.join(input_dir, 'slideshow_with_audio.mp4')
template_folder = args.template_folder + '/'

if video_orientation == 'vertical':
    overlay_video = template_folder + 'name_subscribe_like.mp4'
else:
    overlay_video = template_folder + 'name_subscribe_like_horizontal.mp4'

title = args.title.strip('"')
output_video = os.path.join(input_dir, f"{title.replace(' ', '_')}.mp4")
chromakey_color = args.chromakey_color
chromakey_similarity = args.chromakey_similarity
chromakey_blend = args.chromakey_blend
delay = args.start_delay  # Start time for the overlay (in seconds)
print(f"Start delay: {delay} seconds")

# Handle font color selection
if args.title_fontcolor == 'random':
    fontcolor = random.choice(['FF00B4', 'ff6600', '0b4178'])
else:
    fontcolor = args.title_fontcolor

fontsize = args.title_fontsize

# Get font file path
# fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
fontfile = os.path.join('fonts', args.title_fontfile) if os.path.exists(os.path.join('fonts', args.title_fontfile)) else '/Users/a/Library/Fonts/Montserrat-SemiBold.otf'

# Get overlay video duration using ffprobe
try:
    cmd = f"ffprobe -v error -show_entries format=duration -of json {overlay_video}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    json_data = json.loads(result.stdout)
    overlay_duration = float(json_data['format']['duration'])
    print(f"Overlay video duration: {overlay_duration} seconds")
except Exception as e:
    print(f"Error getting overlay video duration: {e}")
    overlay_duration = 23  # Fallback to default duration if ffprobe fails

print("Overlaying videos...")
step_start = time.time()

# Apply overlay and chromakey to the first part
# Get title appearance parameters
title_appearance_delay = args.title_appearance_delay
title_visible_time = args.title_visible_time

# Calculate when title should appear and disappear
title_start = delay + title_appearance_delay
title_end = title_start + title_visible_time

# Calculate x and y offset
title_x_offset = args.title_x_offset
title_y_offset = args.title_y_offset

overlay_command = [
    'ffmpeg',
    '-loglevel', 'error',
    '-i', input_video,
    '-i', overlay_video,
    '-filter_complex', f"[1:a]adelay={delay*1000}|{delay*1000},volume=0.5[a1];[0:a]volume=1.0[a0];[a0][a1]amix=inputs=2:normalize=0[aout];[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS+{delay}/TB,chromakey=color=0x{chromakey_color}:similarity={chromakey_similarity}:blend={chromakey_blend}[ckout];[v0][ckout]overlay=enable='between(t\,{delay},{delay+overlay_duration})',drawtext=text='{title}':x=((w-tw)/2+{title_x_offset}):y=((h/2)+{title_y_offset}):enable='between(t\,{title_start},{title_end})':fontfile={fontfile}:fontsize={fontsize}:fontcolor=0x{fontcolor}:shadowcolor=black:shadowx=4:shadowy=2:alpha=0.8[out]",
    '-map', '[out]', '-map', '[aout]',
    '-c:v', 'libx264', '-c:a', 'aac', '-y', output_video
]
print(overlay_command)
subprocess.run(overlay_command)

print(f"Name + Subscribe: {time.time() - step_start:.2f} seconds.")

if args.generate_srt == '1':
    print("Adding subtitles...")
    step_start = time.time()
    srt_file = os.path.join(input_dir, 'subs/voiceover.srt')
    srt_styled_output = output_video.replace('.mp4', '_styled.mp4')

    srt_command = [
        'ffmpeg',
        '-loglevel', 'error',
        '-i', output_video,
        '-vf', f"subtitles={srt_file}:force_style='FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=0,Shadow=1,Alignment=2'",
        '-c:a', 'copy',
        '-y', srt_styled_output
    ]

    subprocess.run(srt_command)
    print(f"Subtitles: {time.time() - step_start:.2f} seconds.")

print(f"Finished processing. Output video: {output_video}")
