import os
import shutil
import subprocess
import argparse
import json
from PIL import Image, ImageFilter, ImageDraw
from datetime import datetime


parser = argparse.ArgumentParser()

parser.add_argument('--d', type=int, default=6, dest='segment_duration', help='Duration of each segment (in seconds)')
parser.add_argument('--tl', type=int, default=595, dest='time_limit', help='Duration of clip')
parser.add_argument('--i', type=str, default='INPUT', dest='input_folder', help='Input folder')
parser.add_argument('--n', type=str, default='Model Name', dest='model_name', help='Model name')
parser.add_argument('--f', type=int, default=90, dest='fontsize', help='Font size')
parser.add_argument('--w', type=str, default='Today is a\\n Plus Day', dest='watermark', help='Watermark text')
parser.add_argument('--z', type=str, default='0', dest='depthflow', help='Use DepthFlow for images? 0/1')
parser.add_argument('--o', type=str, default='vertical', dest='video_orientation', help='Video orientation (vertical|horizontal)')
parser.add_argument('--b', type=str, default='0', dest='blur', help='Add blur? 0/1')

args = parser.parse_args()

video_orientation = args.video_orientation

# Function to split a video into segments of X seconds
def split_video(input_file, output_prefix, segment_duration=args.segment_duration):
    try:
        # cmd = f"ffmpeg -i {input_file} -c:v libx265 -crf 22 -map 0 -segment_time {segment_duration} -g {segment_duration} -sc_threshold 0 -force_key_frames expr:gte\(t,n_forced*{segment_duration}\) -f segment -reset_timestamps 1 {output_prefix}%d.mp4"
        # print(f"----- Processing {input_file}")

        cmd = (
            f"ffmpeg -hide_banner -loglevel error -i {input_file} -c:v libx264 -crf 22 -g 30 -r 30 -an "  # Remove audio with -an flag
            f"-map 0 -segment_time {segment_duration} -g {segment_duration} "
            f"-sc_threshold 0 -force_key_frames expr:gte\(t,n_forced*{segment_duration}\) "
            f"-f segment -reset_timestamps 1 {output_prefix}%d.mp4"
        )

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            print(line.decode().strip())
        p.wait()
        if p.returncode != 0:
            raise Exception(f"FFmpeg failed with exit code {p.returncode}")
    
    except Exception as e:
        print(f"Failed to process {input_file}: {e}")

# Input folder containing videos
input_folder = args.input_folder

# Output folder for processed videos
result_folder = os.path.join(input_folder, 'RESULT')

# Create the output folder if it doesn't exist
if not os.path.exists(result_folder):
    os.makedirs(result_folder)

# Create a "SOURCE" subfolder to store original video files after cutting
source_folder = os.path.join(input_folder, 'SOURCE')
if not os.path.exists(source_folder):
    os.makedirs(source_folder)

# Get the current date and time
current_datetime = datetime.now()
datetime_str = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")

# Create the subfolder for the date-time if it doesn't exist
source_date_folder = os.path.join(source_folder, datetime_str)
os.makedirs(source_date_folder, exist_ok=True)



# List all video files in the input folder
video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]

# List all image files in the input folder
image_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg') or f.endswith('.jpeg')]

# List all audio files in the input folder
audio_files = [f for f in os.listdir(input_folder) if f.endswith('.mp3')]

print('##### Video splitting')

# Split each video file into segments
for video_file in video_files:
    input_path = os.path.join(input_folder, video_file)
    
    # ffprobe video to be 16:9 proportion
    cmd = f"ffprobe -v error -show_entries stream=width,height -of json {input_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
    json_data = json.loads(result.stdout)
    width = json_data['streams'][0]['width']
    height = json_data['streams'][0]['height']
    aspect_ratio =  height / width
    
    if abs(aspect_ratio - 16 / 9) > 0.01:
        print(f"Deleting {input_path} as it's not 16:9 aspect ratio")
        os.remove(input_path) # Delete the file
        continue
    else:
        output_prefix = os.path.splitext(os.path.basename(video_file))[0] + '_'

        # input_path is the path to the original video file
        # result_folder is RESULT
        # output_prefix is "filename_"
        # Splitting creates "filename_0.mp4", "filename_1.mp4", etc. in INPUT/RESULT subfolder

        split_video(input_path, os.path.join(result_folder, output_prefix))

        # After splitting - Move original video to the "SOURCE" subfolder
        shutil.move(input_path, os.path.join(source_date_folder, video_file))

print(f'##### Video moved to {result_folder}')

# def resize_image(media_path, target_height):
#     # Function to resize the image
#     image = Image.open(media_path)
#     width, height = image.size
#     target_width = int(width * target_height / height)
#     resized_image = image.resize((target_width, target_height))
#     resized_image.save(media_path)
    
#     if args.video_orientation == 'horizontal' and args.blur == '1':
#         image = Image.open(media_path)

#         # Blur the original image
#         blurred_image = image.filter(ImageFilter.GaussianBlur(10))

#         # Overlay the extracted car onto the blurred image
#         # blurred_image.paste(resized_image, (0, 0), resized_image)

#         # Save the resulting image
#         # blurred_image.save(media_path)
#         # add same image on background blurred and resized image as foreground opacity 100%
#         resized_image = Image.blend(blurred_image, resized_image, 0.5)

#         # Save the resulting image
#         resized_image.save(media_path)
#         return

# def crop_image(media_path, target_width, target_height):
#     # Function to crop the image
#     image = Image.open(media_path)
#     width, height = image.size
#     left = (width - target_width) // 2
#     top = (height - target_height) // 2
#     right = left + target_width
#     bottom = top + target_height
#     cropped_image = image.crop((left, top, right, bottom))
#     cropped_image.save(media_path)



# Set target height
target_height = 1920 if video_orientation == 'vertical' else 1080

def process_image(media_path, target_height, video_orientation):
    # Open the original image
    original_image = Image.open(media_path)
    width, height = original_image.size
    
    # Determine image orientation
    is_vertical_image = height > width
    
    if is_vertical_image:
        
        # Then crop to 9:16
        if video_orientation == 'horizontal':
            # Resize first maintaining aspect ratio
            target_width = target_height * 16 // 9
            calculated_width = int(target_height * width / height)
            resized_image = original_image.resize((calculated_width, target_height), Image.LANCZOS)
            w, h = resized_image.size

            # Create the horizontal gradient mask
            border_width = int(w * 0.1)  # Width of fade effect
            gradient = Image.new('L', (w, h), color=255)
            draw = ImageDraw.Draw(gradient)

            for x in range(border_width):
                fade = int(255 * (x / border_width))
                draw.rectangle([x, 0, x + 1, h], fill=fade)  # Left fade
                draw.rectangle([w - x - 1, 0, w - x, h], fill=fade)  # Right fade

            # Apply gradient as alpha channel
            resized_image.putalpha(gradient)

            # Create blurred background
            background_image = original_image.resize((target_width, target_height), Image.LANCZOS)
            blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))

            # Paste the image with fade onto the background
            x_offset = (target_width - w) // 2
            blurred_background.paste(resized_image, (x_offset, 0), mask=resized_image)
            blurred_background.save(media_path)
            return blurred_background
        
        elif video_orientation == 'vertical':
            # Resize first maintaining aspect ratio
            target_width = target_height * 9 // 16
            calculated_height = int(target_width * height / width)

            resized_image = original_image.resize((target_width, calculated_height), Image.LANCZOS)
            w, h = resized_image.size

            # Create vertical gradient mask
            border_width = int(h * 0.1)
            gradient = Image.new('L', (w, h), color=255)
            draw = ImageDraw.Draw(gradient)
            for y in range(border_width):
                fade = int(255 * (y / border_width))
                draw.rectangle([0, y, w, y + 1], fill=fade)  # Top fade
                draw.rectangle([0, h - y - 1, w, h - y], fill=fade)  # Bottom fade

            resized_image.putalpha(gradient)

            # Create blurred background
            background_image = original_image.resize((target_width, target_height), Image.LANCZOS)
            blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))
            y_offset = (target_height - h) // 2
            blurred_background.paste(resized_image, (0, y_offset), mask=resized_image)
            blurred_background.save(media_path)
            return blurred_background

            # Crop for vertical orientation
            # crop_width = int(target_height * 9 / 16)
            # crop_left = (target_width - crop_width) // 2
            # final_image = resized_image.crop((crop_left, 0, crop_left + crop_width, target_height))
            # final_image.save(media_path)
            # return final_image
    
    elif not is_vertical_image:  # Horizontal image
            
        # Resize first maintaining aspect ratio
        target_width = int(target_height * width / height)
        resized_image = original_image.resize((target_width, target_height), Image.LANCZOS)
        
        if video_orientation == 'vertical':

            target_width = target_height * 9 // 16
            calculated_height = int(target_width * height / width)
            resized_image = original_image.resize((target_width, calculated_height), Image.LANCZOS)
            w, h = resized_image.size

            # Create vertical gradient mask
            border_width = int(h * 0.1)
            gradient = Image.new('L', (w, h), color=255)
            draw = ImageDraw.Draw(gradient)
            for y in range(border_width):
                fade = int(255 * (y / border_width))
                draw.rectangle([0, y, w, y + 1], fill=fade)  # Top fade
                draw.rectangle([0, h - y - 1, w, h - y], fill=fade)  # Bottom fade

            resized_image.putalpha(gradient)

            # Create blurred background
            background_image = original_image.resize((target_width, target_height), Image.LANCZOS)
            blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))
            y_offset = (target_height - h) // 2
            blurred_background.paste(resized_image, (0, y_offset), mask=resized_image)
            blurred_background.save(media_path)
            return blurred_background
        
        elif video_orientation == 'horizontal': # 
            # Crop to 16:9
            target_width = target_height * 16 // 9
            if resized_image.width < target_width:
                
                w, h = resized_image.size

                # Create the horizontal gradient mask
                border_width = int(w * 0.1)  # Width of fade effect
                gradient = Image.new('L', (w, h), color=255)
                draw = ImageDraw.Draw(gradient)

                for x in range(border_width):
                    fade = int(255 * (x / border_width))
                    draw.rectangle([x, 0, x + 1, h], fill=fade)  # Left fade
                    draw.rectangle([w - x - 1, 0, w - x, h], fill=fade)  # Right fade

                # Apply gradient as alpha channel
                resized_image.putalpha(gradient)

                # Create blurred background
                background_image = original_image.resize((target_width, target_height), Image.LANCZOS)
                blurred_background = background_image.filter(ImageFilter.GaussianBlur(radius=20))

                # Paste the image with fade onto the background
                x_offset = (target_width - w) // 2
                blurred_background.paste(resized_image, (x_offset, 0), mask=resized_image)
                blurred_background.save(media_path)
                return blurred_background            
                            
            elif resized_image.width >= target_width:
                # Crop directly if the resized width is sufficient
                crop_left = (resized_image.width - target_width) // 2
                final_image = resized_image.crop((crop_left, 0, crop_left + target_width, target_height))
                final_image.save(media_path)
                return final_image
   
def process_images(input_folder, result_folder, source_date_folder, video_orientation):
    # Set target dimensions based on orientation
    target_height = 1920 if video_orientation == 'vertical' else 1080
    
    # Process each image
    for image_file in os.listdir(input_folder):
        if not image_file.endswith(('.jpg', '.jpeg', '.png')):
            continue
        input_path = os.path.join(input_folder, image_file)
        print(f'Processing {input_path}')
        
        # Copy original to source folder
        if os.path.isfile(input_path):
            shutil.copy(input_path, os.path.join(source_date_folder, image_file))
        
        # Process the image
        process_image(input_path, target_height, video_orientation)
        
        # Move to result folder
        shutil.move(input_path, os.path.join(result_folder, image_file))
    
    print(f'##### Images moved to {result_folder}')

process_images(input_folder, result_folder, source_date_folder, video_orientation)







# # Move each image file to RESULT
# for image_file in image_files:
#     input_path = os.path.join(input_folder, image_file)
    
#     # Copy original image to the "SOURCE" subfolder
#     shutil.copy(input_path, os.path.join(source_date_folder, image_file))

    
#     resize_image(input_path, target_height)
#     crop_image(input_path, target_width, target_height)


#     # Move images to "RESULT" subfolder
#     shutil.move(input_path, os.path.join(result_folder, image_file))

# print(f'##### Images moved to {result_folder}')

# Move each audio file to INPUT/RESULT
for audio_file in audio_files:
    input_path = os.path.join(input_folder, audio_file)

    # Copy original image to the "SOURCE" subfolder
    shutil.copy(input_path, os.path.join(source_date_folder, audio_file))
    
    # Move the original video to the "RESULT" subfolder
    shutil.move(input_path, os.path.join(result_folder, audio_file))

print(f'##### Voiceover moved to {result_folder}')

print(f'##### Delete videos shorter than {args.segment_duration}s')

# After video splitting is completed, run the cleaner.py script with arguments
cleaner_script = 'cleaner.py'  # Replace with the actual filename of your cleaner script
cleaner_args = ['--i', result_folder, '--m', str(args.segment_duration)]  # Arguments to pass to cleaner.py

# Construct the full command to run cleaner.py with arguments
cleaner_command = ['python3', cleaner_script] + cleaner_args

# Run the cleaner.py script with arguments
subprocess.run(cleaner_command)

print(f'##### Rename and move to {result_folder}/{datetime_str}')

# After video cleaning is completed, run the sorter.py script with arguments
sorter_script = 'sorter.py'  # Replace with the actual filename of your sorter script
sorter_args = ['--o', result_folder, '--d', datetime_str]  # Arguments to pass to sorter.py

# Construct the full command to run cleaner.py with arguments
sorter_command = ['python3', sorter_script]  + sorter_args
# sorter_command = ['python3', sorter_script]

# Run the cleaner.py script with arguments
subprocess.run(sorter_command)

print(f'##### Create slideshow {str(args.segment_duration - 1)}s per frame')

# Check if DepthFlow equal 1:

if args.depthflow == '1':

    print("DepthFlow is True")
    depth_script = 'depth.py'  # Replace with the actual filename of your depth script
    depth_args = ['--o', result_folder, '--d', datetime_str, '--t', str(args.segment_duration - 1), '--tl', str(args.time_limit)]

    # Construct the full command to run depth.py with arguments
    depth_command = ['python3', depth_script]  + depth_args

    # Run the depth.py script with arguments
    subprocess.run(depth_command)

# Do the slideshow
slideshow_script = 'slideshow.py'  # Replace with the actual filename of your sorter script
slideshow_args = ['--t', str(args.segment_duration - 1), '--tl', str(args.time_limit), '--n', args.model_name, '--w', args.watermark, '--f', str(args.fontsize), '--z', str(args.depthflow), '--o', str(args.video_orientation)]  # Arguments to pass to slideshow.py

print(slideshow_args)


# Construct the full command to run slideshow.py with arguments
slideshow_command = ['python3', slideshow_script]  + slideshow_args

# Run the slideshow.py script with arguments
subprocess.run(slideshow_command)

print("###### SLIDESHOW READY ######")
