import subprocess
import os
import random
from PIL import Image

def resize_image(image_path, target_height):
    # Function to resize the image
    image = Image.open(image_path)
    width, height = image.size
    target_width = int(width * target_height / height)
    resized_image = image.resize((target_width, target_height))
    resized_image.save(image_path)

def crop_image(image_path, target_width, target_height):
    # Function to crop the image
    image = Image.open(image_path)
    width, height = image.size
    left = (width - target_width) // 2
    top = (height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.save(image_path)

def create_slideshow(folder_path):
    # Function to create the slideshow
    print(f"Processing folder: {folder_path}")
    image_paths = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]
    video_paths = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]

    merged_paths = sorted(image_paths + video_paths, key=lambda x: x.lower())

    if not image_paths:
        print(f"No JPG files found in {folder_path}")
        return

    target_height = 1920
    target_width = 1080

    # Resize and crop images in-place
    for image_path in image_paths:
        print(f"Resizing image: {image_path}")
        resize_image(os.path.join(folder_path, image_path), target_height)
        crop_image(os.path.join(folder_path, image_path), target_width, target_height)

    command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error'
    ]

    # Build the input arguments
    filter_arg = ""

    for j, image_path in enumerate(merged_paths):
        # Zoom-in effect for each image
        filter_arg += f'[{j}]zoompan=z=\'zoom+0.001\':x=iw/2-(iw/zoom/2):y=ih/2-(ih/zoom/2):d=60*6:s=1080x1920[z{j}];'

    for i, image_path in enumerate(merged_paths[:-1]):
        transition_type = random.choice(['hblur', 'smoothup', 'horzopen', 'circleopen', 'diagtr', 'diagbl'])
        offset = (i+1) * 6 - 0.5

        # Crossfade effect between images and videos
        if image_path.endswith('.jpg'):
            filter_arg += f'[z{i}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset}[f{i}];'
        else:
            filter_arg += f'[f{i-1}][z{i + 1}]xfade=transition={transition_type}:duration=0.5:offset={offset}[f{i}];'

    print("FILTER:", filter_arg, "\n\n");
    command.extend(['-r', '30'])

    for i, file_path in enumerate(merged_paths):
        file_extension = os.path.splitext(file_path)[1].lower()
        
        # Check if the file has an image extension
        if file_extension in ('.jpg', '.jpeg'):
            # Add input arguments for an image
            command.extend(['-loop', '1', '-t', '6', '-color_range', 'jpeg', '-i', os.path.join(folder_path, file_path)])
        
        # Check if the file has a video extension
        elif file_extension == '.mp4':
            # Add input arguments for a video
            command.extend(['-i', os.path.join(folder_path, file_path)])
        
        # Handle other file types or unsupported extensions
        else:
            print(f"Skipping file {file_path} with unsupported extension")

    max_duration = len(merged_paths) * 6  # 6 seconds for every image or video
    max_frames = max_duration * 30  #  30 frames per second

    command.extend(['-filter_complex', filter_arg, '-pix_fmt', 'yuv420p', '-color_range', 'jpeg', '-vcodec', 'libx264', '-frames:v', str(max_frames), os.path.join(folder_path, 'slideshow.mp4')])

    try:
        subprocess.run(command, check=True)
        print("FFMPEG: ", command, "\n\n");

        print(f"FFmpeg command executed successfully. Slideshow saved.")
    except subprocess.CalledProcessError as error:
        print("Error executing FFmpeg command:", error)

# Traverse all inner folders
root_folder = 'img'


for folder_name in os.listdir(root_folder):
    folder_path = os.path.join(root_folder, folder_name)
    if os.path.isdir(folder_path):
        create_slideshow(folder_path)
