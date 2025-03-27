import os
import subprocess
import json

# Function to get detailed video info using ffprobe
def get_detailed_video_info(input_file):
    try:
        # Run ffprobe to get detailed codec info of the video stream
        cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,bit_rate,width,height,profile -show_format -of json {input_file}"
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = result.stdout.decode('utf-8')

        # Parse the ffprobe JSON output
        video_info = json.loads(output)
        stream_info = video_info['streams'][0] if 'streams' in video_info else {}
        format_info = video_info['format'] if 'format' in video_info else {}

        codec_name = stream_info.get('codec_name', 'unknown')
        profile = stream_info.get('profile', 'unknown')
        bit_rate = stream_info.get('bit_rate', 'unknown')
        width = stream_info.get('width', 'unknown')
        height = stream_info.get('height', 'unknown')
        duration = format_info.get('duration', 'unknown')
        size = format_info.get('size', 'unknown')

        return codec_name, profile, bit_rate, width, height, duration, size
    except Exception as e:
        print(f"Error checking codec for {input_file}: {e}")
        return None, None, None, None, None, None, None

# Function to print detailed info for all video files in a folder
def print_detailed_video_info_in_folder(folder_path):
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Create the full file path
        file_path = os.path.join(folder_path, file_name)
        
        # Check if it's a file (not a folder) and ends with a video extension
        if os.path.isfile(file_path) and file_name.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv')):
            codec, profile, bit_rate, width, height, duration, size = get_detailed_video_info(file_path)
            if codec:
                print(f"File: {file_name}")
                print(f"  Codec: {codec}")
                print(f"  Profile: {profile}")
                print(f"  Bitrate: {bit_rate} bits/s")
                print(f"  Resolution: {width}x{height}")
                print(f"  Duration: {duration} seconds")
                print(f"  Size: {size} bytes")
                print("-" * 30)

# Folder containing the videos
folder_path = "/Users/a/Desktop/Share/YT/Scripts/VideoCutter/INPUT"

# Call the function to print detailed video info
print_detailed_video_info_in_folder(folder_path)
