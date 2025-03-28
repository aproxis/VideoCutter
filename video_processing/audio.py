"""
Audio processing module for VideoCutter.

This module provides functions for processing audio, including adding audio to videos,
mixing audio tracks, and applying effects.
"""

import os
import subprocess
from typing import Optional, Tuple

from .config import VideoConfig


class AudioProcessor:
    """Class for processing audio."""
    
    def __init__(self, config: VideoConfig):
        """Initialize the AudioProcessor.
        
        Args:
            config: The configuration object.
        """
        self.config = config
        
        # Define template paths
        self.template_folder = 'TEMPLATE'
        self.soundtrack_path = os.path.join(self.template_folder, 'soundtrack.mp3')
        self.voiceover_end_path = os.path.join(self.template_folder, 'voiceover_end.mp3')
        self.transition_sound_path = os.path.join(self.template_folder, 'transition_long.mp3')
    
    def get_video_duration(self, video_path: str) -> float:
        """Get the duration of a video in seconds.
        
        Args:
            video_path: Path to the video file.
            
        Returns:
            The duration in seconds.
            
        Raises:
            subprocess.CalledProcessError: If ffprobe fails.
        """
        ffprobe_command = [
            'ffprobe', '-i', video_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'
        ]
        
        duration_str = subprocess.check_output(ffprobe_command, stderr=subprocess.STDOUT, text=True)
        return float(duration_str)
    
    def cut_soundtrack(self, soundtrack_path: str, output_path: str, duration: float) -> None:
        """Cut the soundtrack to match the video duration.
        
        Args:
            soundtrack_path: Path to the soundtrack file.
            output_path: Path to save the adjusted soundtrack.
            duration: Duration to cut the soundtrack to.
        """
        soundtrack_cut_command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', soundtrack_path,
            '-ss', '0',  # Start from the beginning of the soundtrack
            '-t', str(duration),  # Cut the soundtrack to match video duration
            '-af', f'afade=t=in:st=0:d=3,afade=t=out:st={duration - 3}:d=3,volume=1',
            '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
            '-ac', '2',  # Set the number of audio channels to 2 (stereo)
            output_path
        ]
        
        subprocess.run(soundtrack_cut_command, check=True)
        print(f"--1-- Cut soundtrack to {duration} seconds.")
    
    def cut_transitions(self, transition_path: str, output_path: str, duration: float) -> None:
        """Cut the transition sounds to match the video duration.
        
        Args:
            transition_path: Path to the transition sound file.
            output_path: Path to save the adjusted transitions.
            duration: Duration to cut the transitions to.
        """
        transition_cut_command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', transition_path,
            '-ss', '0',  # Start from the beginning of the soundtrack
            '-t', str(duration - 13),  # Cut the soundtrack to match video duration minus end screen
            '-af', 'volume=1.6',
            '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
            '-ac', '2',  # Set the number of audio channels to 2 (stereo)
            output_path
        ]
        
        subprocess.run(transition_cut_command, check=True)
        print(f"--2-- Cut transitions to video duration - 13 seconds: {duration - 13}")
    
    def add_blank_audio_to_voiceover(self, voiceover_path: str, output_path: str, blank_duration: float = 5.0) -> None:
        """Add blank audio to the beginning of the voiceover.
        
        Args:
            voiceover_path: Path to the voiceover file.
            output_path: Path to save the adjusted voiceover.
            blank_duration: Duration of blank audio to add in seconds.
        """
        voiceover_blank_command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-f', 'lavfi', '-t', str(blank_duration), '-i', 'anullsrc=r=44100:cl=stereo',
            '-i', voiceover_path,
            '-filter_complex', '[0][1]concat=n=2:v=0:a=1[v]',
            '-map', '[v]',
            '-ac', '2',  # Set the number of audio channels to 2 (stereo)
            output_path
        ]
        
        subprocess.run(voiceover_blank_command, check=True)
        print(f"--3-- Added {blank_duration} seconds to voiceover.")
    
    def add_silence_to_audio(self, audio_path: str, output_path: str, target_duration: float) -> None:
        """Add silence to the end of an audio file to match a target duration.
        
        Args:
            audio_path: Path to the audio file.
            output_path: Path to save the extended audio.
            target_duration: Target duration in seconds.
        """
        # Get the duration of the audio file
        audio_duration = self.get_audio_duration(audio_path)
        silence_duration = target_duration - audio_duration
        
        if silence_duration <= 0:
            # If the audio is already longer than the target, just copy it
            shutil.copy(audio_path, output_path)
            return
        
        silence_command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-f', 'lavfi', '-t', str(silence_duration), '-i', 'anullsrc=r=44100:cl=stereo',
            '-i', audio_path,
            '-filter_complex', '[1][0]concat=n=2:v=0:a=1[v]',
            '-map', '[v]',
            '-ac', '2',  # Set the number of audio channels to 2 (stereo)
            output_path
        ]
        
        subprocess.run(silence_command, check=True)
        print(f"--5-- Added {round(silence_duration, 2)} seconds of silence to audio.")
    
    def get_audio_duration(self, audio_path: str) -> float:
        """Get the duration of an audio file in seconds.
        
        Args:
            audio_path: Path to the audio file.
            
        Returns:
            The duration in seconds.
        """
        ffprobe_command = [
            'ffprobe', '-i', audio_path, '-show_entries', 'format=duration', '-v', 'quiet', '-of', 'csv=p=0'
        ]
        
        duration_str = subprocess.check_output(ffprobe_command, stderr=subprocess.STDOUT, text=True)
        return float(duration_str)
    
    def apply_sidechain_compression(self, music_path: str, voice_path: str, output_path: str) -> None:
        """Apply sidechain compression to music using voice as the key input.
        
        Args:
            music_path: Path to the music file.
            voice_path: Path to the voice file.
            output_path: Path to save the compressed audio.
        """
        sidechain_command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', music_path,
            '-i', voice_path,
            '-filter_complex', '[1:a]asplit=2[sc][mix];[0:a][sc]sidechaincompress=ratio=3:threshold=0.02:attack=20:release=500[compr];[compr][mix]amix=normalize=0[compout]',
            '-map', '[compout]',
            '-q:a', '0',  # Set audio quality (0-9, 0 is the best)
            '-ac', '2',  # Set the number of audio channels to 2 (stereo)
            output_path
        ]
        
        subprocess.run(sidechain_command, check=True)
        print(f"--6-- Mixed soundtrack with voiceover using compressor.")
    
    def mix_audio_tracks(self, audio1_path: str, audio2_path: str, output_path: str) -> None:
        """Mix two audio tracks together.
        
        Args:
            audio1_path: Path to the first audio file.
            audio2_path: Path to the second audio file.
            output_path: Path to save the mixed audio.
        """
        mix_command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', audio1_path,
            '-i', audio2_path,
            '-filter_complex', '[0:a]volume=2.0[a0];[1:a]volume=2.0[a1];[a0][a1]amix=inputs=2:normalize=0[aout]',
            '-map', '[aout]',
            output_path
        ]
        
        subprocess.run(mix_command, check=True)
        print(f"--9-- Mixed audio tracks.")
    
    def add_audio_to_video(self, video_path: str, audio_path: str, output_path: str) -> None:
        """Add audio to a video.
        
        Args:
            video_path: Path to the video file.
            audio_path: Path to the audio file.
            output_path: Path to save the video with audio.
        """
        command = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', video_path,
            '-i', audio_path,
            '-map', '0:v',
            '-map', '1:a',
            '-pix_fmt', 'yuv420p',
            '-c:v', 'copy',  # Copy the video codec
            '-c:a', 'aac',  # AAC audio codec
            '-strict', 'experimental',
            '-shortest',  # Ensure the output video duration matches the shortest audio
            output_path
        ]
        
        subprocess.run(command, check=True)
        print(f"+++++ Audio added to the video: {output_path}")
    
    def process_audio(self, directory: str) -> None:
        """Process audio for a slideshow.
        
        Args:
            directory: Path to the directory containing the slideshow.
        """
        slideshow_video_path = os.path.join(directory, 'slideshow.mp4')
        output_video_path = os.path.join(directory, 'slideshow_with_audio.mp4')
        voiceover_path = os.path.join(directory, 'voiceover.mp3')
        
        # Get the duration of the slideshow video
        duration = self.get_video_duration(slideshow_video_path)
        
        # Temporary file paths
        soundtrack_adjusted_path = os.path.join(directory, 'adjusted_soundtrack.mp3')
        transition_adjusted_path = os.path.join(directory, 'adjusted_transitions.mp3')
        voiceover_adjusted_path = os.path.join(directory, 'adjusted_voiceover.mp3')
        voiceover_long_adjusted_path = os.path.join(directory, 'adjusted_long_voiceover.mp3')
        compressed_soundtrack_path = os.path.join(directory, 'compressed_soundtrack.mp3')
        voiceover_end_long_path = os.path.join(directory, 'voiceover_end_long.mp3')
        compressed_end_soundtrack_path = os.path.join(directory, 'compressed_end_soundtrack.mp3')
        mixed_audio_path = os.path.join(directory, 'mixed_audio.mp3')
        
        # Step 1: Cut the soundtrack to match the video duration
        self.cut_soundtrack(self.soundtrack_path, soundtrack_adjusted_path, duration)
        
        # Step 2: Cut the transition sounds
        self.cut_transitions(self.transition_sound_path, transition_adjusted_path, duration)
        
        # Step 3: Add blank audio to the beginning of the voiceover
        self.add_blank_audio_to_voiceover(voiceover_path, voiceover_adjusted_path)
        
        # Step 4: Add silence to the voiceover to match the duration
        vo_duration = self.get_audio_duration(voiceover_adjusted_path)
        print(f"--4-- Duration of adjusted_voiceover: {vo_duration} seconds")
        self.add_silence_to_audio(voiceover_adjusted_path, voiceover_long_adjusted_path, duration)
        
        # Step 5: Apply sidechain compression to the soundtrack using the voiceover
        self.apply_sidechain_compression(soundtrack_adjusted_path, voiceover_long_adjusted_path, compressed_soundtrack_path)
        
        # Step 6: Add silence to the end voiceover
        silence_end_duration = duration - 15
        self.add_silence_to_audio(self.voiceover_end_path, voiceover_end_long_path, duration)
        print(f"--7-- Added {round(silence_end_duration, 2)} seconds of silence to end voiceover.")
        
        # Step 7: Apply sidechain compression to the soundtrack using the end voiceover
        self.apply_sidechain_compression(compressed_soundtrack_path, voiceover_end_long_path, compressed_end_soundtrack_path)
        
        # Step 8: Mix the compressed soundtrack and transitions
        self.mix_audio_tracks(compressed_end_soundtrack_path, transition_adjusted_path, mixed_audio_path)
        
        # Step 9: Add the mixed audio to the video
        self.add_audio_to_video(slideshow_video_path, mixed_audio_path, output_video_path)
