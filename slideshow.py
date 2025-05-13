import subprocess
import os
import argparse
import random
from PIL import Image
import time

# Start timing the entire process
start_time = time.time()


# Create an ArgumentParser to handle command-line arguments
parser = argparse.ArgumentParser(description="Create slideshow.")
parser.add_argument('--sd', type=int, default=5, dest='slide_time', help='Frame duration (in seconds)')
parser.add_argument('--tl', type=int, default=595, dest='time_limit', help='Duration of clip')
parser.add_argument('--od', type=int, default=14, dest='outro_duration', help='Outro duration (in seconds)')

parser.add_argument('--tpl', type=str, default='TEMPLATE', dest='template_folder', help='Template folder')


parser.add_argument('--t', type=str, default='Model Name', dest='title', help='Video title')
parser.add_argument('--tfs', type=int, default=90, dest='title_fontsize', help='Title font size')
parser.add_argument('--tf', type=str, default='Montserrat-SemiBold.otf', dest='title_fontfile', help='Font file name')
parser.add_argument('--tfc', type=str, default='random', dest='title_fontcolor', help='Font color (hex code without #, or "random")')
parser.add_argument('--osd', type=int, default=21, dest='start_delay', help='Delay before title+subscribe overlay appears (in seconds)')
parser.add_argument('--tad', type=int, default=1, dest='title_appearance_delay', help='Delay before title appears (in seconds)')
parser.add_argument('--tvt', type=int, default=5, dest='title_visible_time', help='Duration title remains visible (in seconds)')
parser.add_argument('--tyo', type=int, default=-35, dest='title_y_offset', help='Title y offset')
parser.add_argument('--txo', type=int, default=110, dest='title_x_offset', help='Title x offset')

parser.add_argument('--vd', type=int, default=5, dest='vo_delay', help='Voiceover start delay (in seconds)')


parser.add_argument('--w', type=str, default='Today is a\\n Plus Day', dest='watermark', help='Watermark text')
parser.add_argument('--wf', type=str, default='Nexa Bold.otf', dest='watermark_font', help='Font file name')
parser.add_argument('--wt', type=str, default='random', dest='watermark_type', help='Watermark type: ccw, random')
parser.add_argument('--ws', type=int, default=50, dest='watermark_speed', help='Watermark speed (in frames: 25 = 1s)')


parser.add_argument('--z', type=str, default='0', dest='depthflow', help='Use DepthFlow for images? 1/0')
parser.add_argument('--o', type=str, default='vertical', dest='video_orientation', help='Video orientation (vertical|horizontal)')

parser.add_argument('--chr', type=str, default='65db41', dest='chromakey_color', help='Chromakey color (hex code without #)')
parser.add_argument('--cs', type=float, default=0.18, dest='chromakey_similarity', help='Chromakey similarity (0-1)')
parser.add_argument('--cb', type=float, default=0, dest='chromakey_blend', help='Chromakey blend (0-1)')

parser.add_argument('--srt', type=str, default='0', dest='generate_srt', help='Generate .srt subtitles? 0/1')
parser.add_argument('--smaxw', type=int, default=21, dest='subtitle_max_width', help='Maximum characters in one line of subtitles')


# Parse the command-line arguments
args = parser.parse_args()
args.watermark = args.watermark.replace('\\n', '\n')

video_orientation = args.video_orientation

slide_time = args.slide_time

template_folder = args.template_folder + '/'
# Set target height and width
if video_orientation == 'vertical':
    target_height = 1920
    target_width = 1080
    outro_video_path = template_folder + 'outro_vertical.mp4'

else:
    target_height = 1080
    target_width = 1920
    outro_video_path = template_folder + 'outro_horizontal.mp4'

print(f"******* Using outro video path: {outro_video_path}")  # Print the full path

# print os path of current folder
print(f"******* Current folder path: {os.path.abspath(os.getcwd())}")


def create_slideshow(folder_path):
    # Function to create the slideshow

    # Get the list of image and video files in the folder
    print(f"+++++ Processing folder: {folder_path}")
    print(f"Using outro video path: {os.path.abspath(outro_video_path)}")  # Print the full path of the outro video

    image_paths = [f for f in os.listdir(folder_path) if f.endswith('.jpg') or f.endswith('.jpeg')]
    
    # if depthflow is equal 1 - remove all images from list image_path
    
    if args.depthflow == '1':
        image_paths = []
        print(f"***** Not using JPG files, using DepthFlow. {folder_path}")

    
    video_paths = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]


    # Sort the image and video paths alphabetically
    merged_paths = sorted(image_paths + video_paths, key=lambda x: x.lower())
    merged_paths_orig = merged_paths

    # limit number of values in "merged_paths"
    limit = int(args.time_limit/args.slide_time - 3)
    merged_paths = merged_paths[:limit]


    # show difference between "merged_paths" and "merged_paths_limit"
    print(f"***** Number of values in merged_paths: {len(merged_paths)}")
    print(f"***** Number of values in merged_paths_orig: {len(merged_paths_orig)}")


    # Add outro.mp4 to the end of the list
    if not os.path.isfile(outro_video_path):
        print(f"***** Error: Outro video file does not exist at {outro_video_path}. Skipping slideshow creation.")
        return
    else:
        merged_paths.append(os.path.abspath(outro_video_path))
        print(merged_paths)

    # Check if there are any JPG files
    if not image_paths:
        print(f"***** No JPG files found in {folder_path}")
        # return

    # Set target height and width
    # target_height = 1920
    # target_width = 1080

    # Set frame rate
    fps = 25

    # Set watermark text and opacity
    watermark_text = args.watermark
    watermark_type = args.watermark_type

    watermark_opacity = 0.7
    wmTimer = args.watermark_speed # 50 - every half-slide move watermark
 
    # Set font file and font size
    # Try to find the font in the fonts directory
    watermark_font_path = os.path.join('fonts', args.watermark_font)
    if os.path.exists(watermark_font_path):
        watermark_fontfile = os.path.abspath(watermark_font_path)
    else:
        # Fallback: try to find any font in the fonts directory
        fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
        available_fonts = [f for f in os.listdir(fonts_dir) if f.endswith('.ttf') or f.endswith('.otf')]
        if available_fonts:
            watermark_fontfile = os.path.join(fonts_dir, available_fonts[0])
        else:
            # Last resort: try to find Nexa font in the system
            try:
                watermark_fontfile = subprocess.run(['fc-list', ':family', 'Nexa'], check=True, capture_output=True).stdout.decode().strip().split(':')[0]
            except:
                print("***** Error: Could not find any font. Using default system font.")
                watermark_fontfile = ""
    
    # print font
    print(f"***** Using font: {watermark_fontfile}")
    watermark_fontsize = 40

    # Set up FFMPEG command
    command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'
    ]

    # Build the input arguments
    filter_arg = ""

    for j, media_path in enumerate(merged_paths):

        # Zoom-in effect for each image
        if media_path.endswith('.jpg'):
            filter_arg += f'[{j}]zoompan=z=\'zoom+0.001\':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=30*{slide_time}:s={target_width}x{target_height}[z{j}];'

        # Adjust video input parameters to match
        if media_path.endswith('.mp4'):
            if "outro.mp4" in media_path.lower():
                filter_arg += f'[{j}]settb=AVTB,setpts=PTS-STARTPTS,fps={fps}/1,setsar=1:1[z{j}];'
            else:
                filter_arg += f'[{j}]settb=AVTB,setpts=PTS-STARTPTS,fps={fps}/1,scale={target_width}:{target_height},setsar=1:1[z{j}];'


    for i, media_path in enumerate(merged_paths[:-1]):

        # Transitions
        transition_type = random.choice(['hblur', 'smoothup', 'horzopen', 'circleopen', 'diagtr', 'diagbl'])
     
        # Calculate offset for transitions
        offset = (i+1) * slide_time - 0.5

        if i == 0:
            # Crossfade effect between the first two images
   
            filter_arg += f'[z{i}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset}[f{i}];'
     
        
        elif i == len(merged_paths[:-1]) - 1:
            
            # No chaining for last image in sequence - no semicolon in the end!!!
            
            filter_arg += f'[f{i-1}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset}'

        else:
            # Crossfade effect between intermediate media and watermark
            if watermark_type == 'ccw':

                filter_arg += (
                    f'[f{i-1}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset},'
                    f'drawtext=text=\'{watermark_text}\':'
                    f'x=\'if(lt(mod(n/{wmTimer},4),1),15+mod(n/{wmTimer},1)*(w-text_w-30),if(lt(mod(n/{wmTimer},4),2),w-text_w-15,if(lt(mod(n/{wmTimer},4),3),w-text_w-15-(mod(n/{wmTimer},1)*(w-text_w-30)),15)))\':\
                    y=\'if(lt(mod(n/{wmTimer},4),1),15,if(lt(mod(n/{wmTimer},4),2),15+mod(n/{wmTimer},1)*(h-text_h-30),if(lt(mod(n/{wmTimer},4),3),h-text_h-15,h-text_h-15-(mod(n/{wmTimer},1)*(h-text_h-30)))))\':\
                    fontfile={watermark_fontfile}:fontsize={watermark_fontsize}:fontcolor_expr=random@{watermark_opacity}[f{i}];'
            )
            
            elif watermark_type == 'random':

                filter_arg += f'[f{i-1}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset},drawtext=text=\'{watermark_text}\':x=if(eq(mod(n\,{wmTimer})\,0)\,random(1)*w\,x):y=if(eq(mod(n\,{wmTimer})\,0)\,random(1)*h\,y):fontfile={watermark_fontfile}:fontsize={watermark_fontsize}:fontcolor_expr=random@{watermark_opacity}[f{i}];'

            

               

    # print("FILTER:", filter_arg, "\n\n");
    
    # Set framerate of output video
    command.extend(['-r', str(fps)])

    # Set input arguments
    image_extensions = ['.jpg', '.jpeg']
    video_extensions = ['.mp4']

    for i, file_path in enumerate(merged_paths):
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Check if the file is named "outro.mp4" and has a video extension
        if "outro.mp4" in file_path.lower() and file_extension in video_extensions:

            # Add input arguments for the "outro.mp4" video
            command.extend(['-i', file_path])
        else:
            # Check if the file has an image extension
            if file_extension in image_extensions:
                # Add input arguments for an image
                command.extend(['-loop', '1', '-t', str(slide_time), '-color_range', 'jpeg', '-i', os.path.join(folder_path, file_path)])
            
            # Check if the file has a video extension
            elif file_extension in video_extensions:
                # Add input arguments for a video
                command.extend(['-i', os.path.join(folder_path, file_path)])
            
            # Handle other file types or unsupported extensions
            else:
                print(f"Skipping file {file_path} with unsupported extension")


    max_duration = len(merged_paths) * slide_time + (args.outro_duration - slide_time) # 5 seconds for every image: maximum duration in seconds to limit infinite loop adding last image infinitely; +(14 - slide_time) is for outro.mp4, it's 14 seconds long
    print(f"***** Number of values in merged_paths: {len(merged_paths)}, {slide_time} seconds per image, {args.outro_duration} seconds for outro.mp4")
    print(f"***** Max duration: {max_duration} seconds")

    max_frames = max_duration * fps  #  25 frames per second

    command.extend(['-filter_complex', filter_arg, '-pix_fmt', 'yuv420p', '-color_range', 'jpeg', '-vcodec', 'libx264', '-frames:v', str(max_frames), '-b:v', '2000k', os.path.join(folder_path, 'slideshow.mp4')])

    try:
        print(f"##### Creating slideshow")

        subprocess.run(command, check=True)
        # print("FFMPEG: ", command, "\n\n")

        print(f"+++++ Slideshow saved: {folder_path}/slideshow.mp4")


        # Add audio
        print(f"##### Adding audio")
        
        audio_script = 'audio.py' 
        audio_args = [
            '--i', folder_path, 
            '--od', str(args.outro_duration),
            '--vd', str(args.vo_delay),
            '--srt', args.generate_srt,
            '--smaxw', str(args.subtitle_max_width),
        ]
        audio_command = ['python3', audio_script]  + audio_args
        subprocess.run(audio_command, check=True)

        
        # Add subscribe overlay
        print(f"##### Adding name, watermark, subscribe overlay")

        
        subscribe_script = 'subscribe.py' 
        subscribe_args = [
            '--i', folder_path, 
            '--tpl', args.template_folder,
            
            '--t', f'"{args.title}"', 
            '--tf', args.title_fontfile,
            '--tfc', args.title_fontcolor, 
            '--tfs', str(args.title_fontsize), 
            '--osd', str(args.start_delay),
            '--tad', str(args.title_appearance_delay),
            '--tvt', str(args.title_visible_time),
            '--txo', str(args.title_x_offset),
            '--tyo', str(args.title_y_offset),

            '--o', str(args.video_orientation),
            '--chr', args.chromakey_color,
            '--cs', str(args.chromakey_similarity),
            '--cb', str(args.chromakey_blend),

            '--srt', args.generate_srt,

        ]
        
        subscribe_command = ['python3', subscribe_script]  + subscribe_args
        subprocess.run(subscribe_command, check=True)

        print(f"+++++ Subscribe overlay added.")

    except subprocess.CalledProcessError as error:
        # print("***** Error executing FFmpeg command:", error) 
        print("***** Error executing FFmpeg command")

# Traverse all inner folders
root_folder = 'INPUT/RESULT'

for folder_name in os.listdir(root_folder):
    folder_path = os.path.join(root_folder, folder_name)

    # if there is slideshow.mp4 file, skip it
    if os.path.isfile(os.path.join(folder_path, 'slideshow.mp4')):
        print(f"----- Slideshow already exists in {folder_path}")
        continue
    elif os.path.isdir(folder_path):
        create_slideshow(folder_path)

print(f"Slideshow creation complete: {time.time() - start_time:.2f} seconds.")
