import subprocess
import os
import random
import argparse
import time
import json
import glob
from fontTools.ttLib import TTFont

# Function to extract font name from font file
def get_font_name(font_path):
    try:
        font = TTFont(font_path)
        name = ''
        for record in font['name'].names:
            if record.nameID == 4:  # Full font name
                try:
                    name = record.string.decode(record.getEncoding())
                except:
                    name = record.string.decode('utf-8', errors='ignore')
                break
        font.close()
        return name
    except Exception as e:
        print(f"Error extracting font name: {e}")
        return os.path.basename(font_path).split('.')[0]  # Fallback to filename without extension

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

# Subtitle arguments
parser.add_argument('--srt', type=str, default='0', dest='generate_srt', help='Add SRT subtitles? 0/1')
parser.add_argument('--sf', type=str, default='Arial', dest='subtitle_font', help='Font for subtitles')
parser.add_argument('--sfs', type=int, default=24, dest='subtitle_fontsize', help='Subtitle font size')
parser.add_argument('--sfc', type=str, default='FFFFFF', dest='subtitle_fontcolor', help='Subtitle font color (hex without #)')
parser.add_argument('--sbc', type=str, default='000000', dest='subtitle_bgcolor', help='Subtitle shadow color (hex without #)')
parser.add_argument('--sbo', type=float, default=0.5, dest='subtitle_bgopacity', help='Subtitle shadow opacity (0-1)')
parser.add_argument('--spos', type=int, default=2, dest='subtitle_position', help='Subtitle position (1-9, ASS alignment)')
parser.add_argument('--sout', type=float, default=1, dest='subtitle_outline', help='Subtitle outline thickness')
parser.add_argument('--soutc', type=str, default='000000', dest='subtitle_outlinecolor', help='Subtitle outline color (hex without #)')
parser.add_argument('--shadow', type=int, default=1, dest='subtitle_shadow', help='Enable subtitle shadow (0/1)')

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

# Prepare subtitle styling if needed
srt_file = None
subtitle_style = None

if args.generate_srt == '1':
    print("Preparing subtitle styling...")
    srt_file = os.path.join(input_dir, 'subs/voiceover.srt')
    
    # Get subtitle font path
    subtitle_font_arg = args.subtitle_font
    # Define fonts directory
    fonts_dir = os.path.join(os.path.dirname(__file__), 'fonts')
    font_files = glob.glob(os.path.join(fonts_dir, '*.[ot]tf'))
    font_names = [os.path.basename(f) for f in font_files]
    
    # Font path and name variables
    font_path = None
    font_name = None
    
    # If the specified font exists in the fonts directory, use it
    if subtitle_font_arg in font_names:
        font_path = os.path.join(fonts_dir, subtitle_font_arg)
    # If it's a font file that exists in the system, use it
    elif os.path.exists(os.path.join('/Users/a/Library/Fonts', subtitle_font_arg)):
        font_path = os.path.join('/Users/a/Library/Fonts', subtitle_font_arg)
    # Otherwise, use the first available font in the fonts directory
    elif font_files:
        font_path = font_files[0]
        print(f"Font '{args.subtitle_font}' not found, using '{os.path.basename(font_path)}' instead.")
    else:
        # Fallback to Arial
        font_path = None
        font_name = "Arial"
        print(f"No fonts found in fonts directory, using system font 'Arial'.")
    
    # Extract the actual font name if we have a font path
    if font_path:
        font_name = get_font_name(font_path)
        print(f"Using font: {font_name} from {font_path}")
    
    # Prepare subtitle styling
    # Base style parameters
    # Convert RGB hex colors to BGR for ASS format
    font_color_bgr = args.subtitle_fontcolor[4:6] + args.subtitle_fontcolor[2:4] + args.subtitle_fontcolor[0:2]
    outline_color_bgr = args.subtitle_outlinecolor[4:6] + args.subtitle_outlinecolor[2:4] + args.subtitle_outlinecolor[0:2]
    shadow_color_bgr = args.subtitle_bgcolor[4:6] + args.subtitle_bgcolor[2:4] + args.subtitle_bgcolor[0:2]
    
    style_params = [
        f"FontName={font_name}",
        f"FontSize={args.subtitle_fontsize}",
        f"PrimaryColour=&H00{font_color_bgr}",
        f"OutlineColour=&H00{outline_color_bgr}",
        f"Outline={args.subtitle_outline}",
        f"Alignment={args.subtitle_position}"
    ]
    
    # Add shadow if enabled (shadow is text shadow, not background)
    if hasattr(args, 'subtitle_shadow') and args.subtitle_shadow:
        # Convert opacity from 0-1 to 00-FF hex (invert the opacity for ASS format)
        opacity_value = int((1.0 - args.subtitle_bgopacity) * 255)
        opacity_hex = format(opacity_value, '02X')
        style_params.append(f"BackColour=&H{opacity_hex}{shadow_color_bgr}")
        style_params.append("Shadow=1")
    else:
        style_params.append("Shadow=0")
    
    # Join all style parameters
    subtitle_style = ",".join(style_params)
    print(f"Subtitle style: {subtitle_style}")

# Build the filter complex based on whether subtitles are needed
filter_complex = f"[1:a]adelay={delay*1000}|{delay*1000},volume=0.5[a1];[0:a]volume=1.0[a0];[a0][a1]amix=inputs=2:normalize=0[aout];[0:v]setpts=PTS-STARTPTS[v0];[1:v]setpts=PTS-STARTPTS+{delay}/TB,chromakey=color=0x{chromakey_color}:similarity={chromakey_similarity}:blend={chromakey_blend}[ckout];[v0][ckout]overlay=enable='between(t\,{delay},{delay+overlay_duration})',drawtext=text='{title}':x=((w-tw)/2+{title_x_offset}):y=((h/2)+{title_y_offset}):enable='between(t\,{title_start},{title_end})':fontfile={fontfile}:fontsize={fontsize}:fontcolor=0x{fontcolor}:shadowcolor=black:shadowx=4:shadowy=2:alpha=0.8"

# Add subtitle filter if needed
if args.generate_srt == '1' and os.path.exists(srt_file):
    # Get absolute path to fonts directory
    abs_fonts_dir = os.path.abspath('fonts')
    filter_complex += f",subtitles={srt_file}:fontsdir='{abs_fonts_dir}':force_style='{subtitle_style}'"

# Complete the filter complex
filter_complex += "[out]"

overlay_command = [
    'ffmpeg',
    '-loglevel', 'error',
    '-i', input_video,
    '-i', overlay_video,
    '-filter_complex', filter_complex,
    '-map', '[out]', '-map', '[aout]',
    '-c:v', 'libx264', '-c:a', 'aac', '-y', output_video
]
print("Executing combined ffmpeg command...")
print(overlay_command)
subprocess.run(overlay_command)

print(f"Processing completed: {time.time() - step_start:.2f} seconds.")

print(f"Finished processing. Output video: {output_video}")
