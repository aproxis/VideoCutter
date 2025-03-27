import subprocess
import os
import argparse
import time

# Start timing the entire process
start_time = time.time()


# Create an ArgumentParser to handle command-line arguments
parser = argparse.ArgumentParser(description="Create slideshow.")
parser.add_argument('--i', dest='path', required=True, help='Path to the directory containing audio and video')


# Parse the command-line arguments
args = parser.parse_args()
directory = args.path

def add_audio_to_video(slideshow_video_path, soundtrack_path, transition_sound_path, voiceover_path, voiceover_end_path, output_video_path):
    # Step 1: Cut the soundtrack and reduce its volume by 50%
    # Get the duration of the slideshow video
    ffprobe_command = [
        'ffprobe', '-i', slideshow_video_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'
    ]
    try:
        duration_str = subprocess.check_output(ffprobe_command, stderr=subprocess.STDOUT, text=True)
        duration = float(duration_str)
    except subprocess.CalledProcessError as error:
        print("***** Error getting video duration:", error)
        return

    soundtrack_adjusted_path = os.path.join(directory, 'adjusted_soundtrack.mp3')
    soundtrack_cut_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', soundtrack_path,
        '-ss', '0',  # Start from the beginning of the soundtrack
        '-t', str(duration),  # Cut the soundtrack to match video duration
        '-af', 'afade=t=in:st=0:d=3,afade=t=out:st=' + str(duration - 3) + ':d=3,volume=1',
        '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        soundtrack_adjusted_path
    ]

    try:
        subprocess.run(soundtrack_cut_command, check=True)
        print(f"--1-- Cutted soundtrack to {duration} seconds.")

    except subprocess.CalledProcessError as error:
        print("***** Error cutting and adjusting soundtrack:", error)
        return


    

    transition_adjusted_path = os.path.join(directory, 'adjusted_transitions.mp3')
    transition_cut_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', transition_sound_path,
        '-ss', '0',  # Start from the beginning of the soundtrack
        '-t', str(duration - 13),  # Cut the soundtrack to match video duration minus end screen
        '-af', 'volume=1.6',
        '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        transition_adjusted_path
    ]

    try:
        subprocess.run(transition_cut_command, check=True)
        print(f"--2-- Cutted transitions to video duration - 13 seconds: ", str(duration - 13))

    except subprocess.CalledProcessError as error:
        print("***** Error cutting and adjusting transition:", error)
        return


    # Step 2: Add 5 seconds of blank audio to the beginning of the voiceover
    voiceover_adjusted_path = os.path.join(directory, 'adjusted_voiceover.mp3')
    voiceover_blank_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-t', '5', '-i', 'anullsrc=r=44100:cl=stereo',
        '-i', voiceover_path,
        '-filter_complex', '[0][1]concat=n=2:v=0:a=1[v]',
        '-map', '[v]',
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        voiceover_adjusted_path
    ]

    try:
        subprocess.run(voiceover_blank_command, check=True)
        print(f"--3-- Added 5 seconds to voiceoiver.")

    except subprocess.CalledProcessError as error:
        print("***** Error adding blank audio to the voiceover:", error)
        return

    # Step 3: Add silence to the voiceover to match the duration of the soundtrack and video
    # Run ffprobe to get the duration of the adjusted voiceover
    vo_ffprobe_command = [
        'ffprobe', '-i', voiceover_adjusted_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'
    ]

    try:
        vo_duration_str = subprocess.check_output(vo_ffprobe_command, stderr=subprocess.STDOUT, text=True)
        vo_duration = float(vo_duration_str)
        print(f"--4-- Duration of adjusted_voiceover: {vo_duration} seconds")
    except subprocess.CalledProcessError as error:
        print("***** Error getting adjusted_voiceover duration:", error)


    silence_duration = duration - vo_duration  # Subtract voiceover length from video duration
    voiceover_long_adjusted_path = os.path.join(directory, 'adjusted_long_voiceover.mp3')
    voiceover_silence_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-t', str(silence_duration), '-i', 'anullsrc=r=44100:cl=stereo',
        '-i', voiceover_adjusted_path,
        '-filter_complex', '[1][0]concat=n=2:v=0:a=1[v]',
        '-map', '[v]',
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        voiceover_long_adjusted_path
    ]

    try:
        subprocess.run(voiceover_silence_command, check=True)
        print(f"--5-- Added {round(silence_duration, 2)} seconds of silence to voiceoiver.")

    except subprocess.CalledProcessError as error:
        print("***** Error adding silence to the voiceover:", error)
        return

    # Step 4: Apply sidechain compression to the soundtrack using the adjusted voiceover as the key input
    compressed_soundtrack_path = os.path.join(directory, 'compressed_soundtrack.mp3')
    sidechain_compression_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', soundtrack_adjusted_path,
        '-i', voiceover_long_adjusted_path,
        '-filter_complex', '[1:a]asplit=2[sc][mix];[0:a][sc]sidechaincompress=ratio=3:threshold=0.02:attack=20:release=500[compr];[compr][mix]amix=normalize=0[compout]',
        # '-filter_complex', '[0:a][1:a]sidechaincompress=threshold=0.015:ratio=19:level_sc=1:release=1400:attack=1[compout]',
        '-map', '[compout]',
        '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        compressed_soundtrack_path
    ]

    try:
        subprocess.run(sidechain_compression_command, check=True)
        print(f"--6-- Mixed soundtrack with voiceoiver using compressor.")

    except subprocess.CalledProcessError as error:
        print("***** Error adding voiceover over the soundtrack:", error)
        return

    silence_end_duration = duration - 15  # Subtract voiceover end length from video duration
    voiceover_end_long_path = os.path.join(directory, 'voiceover_end_long.mp3')
    voiceover_silence_end_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-f', 'lavfi', '-t', str(silence_end_duration), '-i', 'anullsrc=r=44100:cl=stereo',
        '-i', voiceover_end_path,
        '-filter_complex', '[0][1]concat=n=2:v=0:a=1[v]',
        '-map', '[v]',
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        voiceover_end_long_path
    ]

    try:
        subprocess.run(voiceover_silence_end_command, check=True)

        print(f"--7-- Added {round(silence_end_duration, 2)} seconds of silence to end voiceoiver.")

    except subprocess.CalledProcessError as error:
        print("***** Error adding silence to the end voiceover:", error)
        return

    # Step 4.1: Apply sidechain compression to the soundtrack using the adjusted voiceover_end as the key input
    compressed_end_soundtrack_path = os.path.join(directory, 'compressed_end_soundtrack.mp3')
    sidechain_compression_end_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', compressed_soundtrack_path,
        '-i', voiceover_end_long_path,
        '-filter_complex', '[1:a]asplit=2[sc][mix];[0:a][sc]sidechaincompress=ratio=3:threshold=0.02:attack=20:release=500[compr];[compr][mix]amix=normalize=0[compout]',
        # '-filter_complex', '[0:a][1:a]sidechaincompress=threshold=0.015:ratio=19:level_sc=1:release=1400:attack=1[compout]',
        '-map', '[compout]',
        '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
        '-ac', '2',  # Set the number of audio channels to 2 (stereo)
        compressed_end_soundtrack_path
    ]

    try:
        subprocess.run(sidechain_compression_end_command, check=True)
        print(f"--8-- Mixed soundtrack with END voiceoiver using compressor.")

    except subprocess.CalledProcessError as error:
        print("***** Error adding END voiceover over the soundtrack:", error)
        return

    

    # Step 5: Mix the adjusted soundtrack and voiceover together
    # comment this code if you don't want to use voiceover
    mixed_audio_path = os.path.join(directory, 'mixed_audio.mp3')
    audio_mix_command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', compressed_end_soundtrack_path,
        '-i', transition_adjusted_path,
        # '-i', voiceover_adjusted_path,
        # '-filter_complex', '[0:a][1:a]amix=inputs=2[aout]',
        '-filter_complex', '[0:a]volume=2.0[a0];[1:a]volume=2.0[a1];[a0][a1]amix=inputs=2:normalize=0[aout]',
        '-map', '[aout]',
        mixed_audio_path
    ]

    try:
        subprocess.run(audio_mix_command, check=True)
        print(f"--9-- Mixed transitions.")

    except subprocess.CalledProcessError as error:
        print("Error mixing audio:", error)
        return

    
    # Step 5: Replace the original video's audio with the mixed audio
    command = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
        '-i', slideshow_video_path,
        '-i', mixed_audio_path,
        '-map', '0:v',
        '-map', '1:a',
        '-pix_fmt', 'yuv420p',
        '-c:v', 'copy',  # Copy the video codec
        '-c:a', 'aac',  # AAC audio codec
        '-strict', 'experimental',
        '-shortest',  # Ensure the output video duration matches the shortest audio
        output_video_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"+++++ Audio added to the video: {output_video_path}")
    except subprocess.CalledProcessError as error:
        print("***** Error executing FFmpeg command:", error)


# Example usage to add audio to the slideshow video

slideshow_video_path = os.path.join(directory, 'slideshow.mp4')
output_video_path = os.path.join(directory, 'slideshow_with_audio.mp4')
voiceover_path = os.path.join(directory, 'voiceover.mp3')
soundtrack_path = 'TEMPLATE/soundtrack.mp3'
voiceover_end_path = 'TEMPLATE/voiceover_end.mp3'
transition_sound_path = 'TEMPLATE/transition_long.mp3'


add_audio_to_video(slideshow_video_path, soundtrack_path, transition_sound_path, voiceover_path, voiceover_end_path, output_video_path)
print(f"Add Audio: {time.time() - start_time:.2f} seconds.")
