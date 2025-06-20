# main.py - Main orchestrator script
import os
import json
import csv
import logging
import shutil
from pathlib import Path
from datetime import datetime # Added for timestamping

# Import the logging setup function
from .utils.logger_config import setup_logging

from content.youtube_handler import YouTubeHandler
from content.transcript_processor import TranscriptProcessor
from content.image_searcher import ImageSearcher
from content.voice_generator import VoiceGenerator
from content.config import Config

# Get logger for this module
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self, config_path="content/config.json"):
        self.config = Config(config_path)
        # Logging setup is now handled by the GUI
        logger.info("Initializing VideoProcessor...")
        
        self.youtube = YouTubeHandler(self.config)
        self.transcript_processor = TranscriptProcessor(self.config)
        self.image_searcher = ImageSearcher(self.config)
        self.voice_generator = VoiceGenerator(self.config)
        logger.info("VideoProcessor initialized.")
        
    def process_channel(self, channel_url, max_videos=None, generate_voiceover=True, rewrite_transcript=True, download_images=True, seconds_per_image=None, download_pexels_videos=False, num_pexels_videos=0, youtube_filter=""):
        """Process all videos from a YouTube channel"""
        logger.info(f"Processing channel: {channel_url} (max_videos: {max_videos}, voiceover: {generate_voiceover}, rewrite: {rewrite_transcript}, download_images: {download_images}, seconds_per_image: {seconds_per_image}, download_pexels_videos: {download_pexels_videos}, num_pexels_videos: {num_pexels_videos}, youtube_filter: {youtube_filter})")
        
        channel_name = channel_url.split('/')[-1]
        current_datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        # Create top-level output directory for this channel run
        run_output_dir = Path(self.config.output_dir) / f"{current_datetime_str}_channel_{channel_name}"
        run_output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Top-level output directory created: {run_output_dir}")

        # Get videos from channel, passing the new output_base_dir
        videos, csv_filepath = self.youtube.get_channel_videos(channel_url, run_output_dir, max_videos)
        
        # This method now only searches and returns, it does not process videos
        return videos, csv_filepath, run_output_dir

    def process_search_results(self, search_query, max_videos=50, generate_voiceover=True, rewrite_transcript=True, download_images=True, seconds_per_image=None, download_pexels_videos=False, num_pexels_videos=0, youtube_filter=""):
        """Search for videos and return results. Does not process them."""
        logger.info(f"Searching YouTube for: '{search_query}' (max_videos: {max_videos}, youtube_filter: {youtube_filter})")
        
        formatted_query = search_query.replace(" ", "_")
        current_datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Create top-level output directory for this search run
        run_output_dir = Path(self.config.output_dir) / f"{current_datetime_str}_search_{formatted_query}"
        run_output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Top-level output directory created: {run_output_dir}")

        # Get videos from search, passing the new output_base_dir
        videos, csv_filepath = self.youtube.search_videos(search_query, run_output_dir, max_videos, youtube_filter=youtube_filter)
        
        # This method now only searches and returns, it does not process videos
        return videos, csv_filepath, run_output_dir

    def process_single_video(self, video_url, generate_voiceover=True, rewrite_transcript=True, download_images=True, seconds_per_image=None, download_pexels_videos=False, num_pexels_videos=0):
        """Process a single video from its URL."""
        logger.info(f"Processing single video: {video_url}")
        
        video_info = self.youtube.get_video_info_from_url(video_url)
        if not video_info:
            logger.error(f"Could not get info for single video URL: {video_url}. Skipping processing.")
            return [], None, None # Return empty list, None, None to match other search results

        # Create a temporary run_output_dir for single video processing
        current_datetime_str = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        run_output_dir = Path(self.config.output_dir) / f"{current_datetime_str}_single_video_{video_info['id']}"
        run_output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Temporary output directory created for single video: {run_output_dir}")

        # This method now only fetches video info and creates the run_output_dir
        # Actual processing will be triggered by the GUI's process buttons
        return [video_info], None, run_output_dir # Return as a list for consistency

    def _process_videos_list(self, videos_to_process, run_output_dir, generate_voiceover, rewrite_transcript, download_images, seconds_per_image, download_pexels_videos, num_pexels_videos, rewrite_prompt=None):
        """Internal method to process a given list of video_info dictionaries."""
        logger.info(f"Starting processing for {len(videos_to_process)} video(s) in run_output_dir: {run_output_dir}")
        
        processed_videos_data = []
        for video_info in videos_to_process:
            original_transcript, rewritten_transcript = self.process_video(
                video_info,
                run_output_dir,
                generate_voiceover=generate_voiceover,
                rewrite_transcript=rewrite_transcript,
                download_images=download_images,
                seconds_per_image=seconds_per_image,
                download_pexels_videos=download_pexels_videos,
                num_pexels_videos=num_pexels_videos,
                rewrite_prompt=rewrite_prompt # Pass the custom rewrite prompt
            )
            if original_transcript: # Only add if processing was successful and transcript exists
                video_data = video_info.copy()
                video_data['original_transcript'] = original_transcript
                video_data['rewritten_transcript'] = rewritten_transcript
                processed_videos_data.append(video_data)
        
        logger.info(f"Finished processing {len(videos_to_process)} video(s).")

        # Write combined data to CSV
        if processed_videos_data:
            csv_filepath = run_output_dir / "processed_videos_summary.csv"
            with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'title', 'url', 'duration', 'published_at', 'description', 'original_transcript', 'rewritten_transcript']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(processed_videos_data)
            logger.info(f"Combined video data saved to {csv_filepath}")
        else:
            logger.warning("No videos were successfully processed, so no combined CSV was generated.")

    def close(self):
        """Clean up resources"""
        logger.info("Closing VideoProcessor resources...")
        self.youtube.close()
        logger.info("VideoProcessor resources closed.")
    
    def process_video(self, video_info, run_output_dir, generate_voiceover=True, rewrite_transcript=True, download_images=True, seconds_per_image=None, download_pexels_videos=False, num_pexels_videos=0, rewrite_prompt=None):
        """Process a single video"""
        video_id = video_info['id']
        title = video_info['title']
        duration = int(video_info['duration']) # Force duration to be an integer
        
        # Use provided seconds_per_image or fallback to config
        effective_seconds_per_image = seconds_per_image if seconds_per_image is not None else self.config.seconds_per_image
        effective_seconds_per_image = int(effective_seconds_per_image) # Ensure it's an integer
        
        logger.info(f"Starting processing for video: {title} (ID: {video_id})")
        
        # Create output directory nested under the run_output_dir
        output_dir = run_output_dir / f"{video_id}_{title[:50]}"
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory created: {output_dir}")
        
        try:
            # Get transcript using the dedicated fetcher
            transcript = self.youtube.fetch_transcript_for_video(video_id)
            if not transcript:
                logger.warning(f"No transcript available for {title} (ID: {video_id}). Skipping video processing.")
                return None, None # Return None, None to match other return paths
            
            logger.info(f"Transcript fetched for {title}. Length: {len(transcript)} characters.")
            # Save original transcript
            with open(output_dir / "original_transcript.txt", "w", encoding="utf-8") as f:
                f.write(transcript)
            logger.info("Original transcript saved.")
            
            processed_text = transcript
            if rewrite_transcript:
                # Use provided rewrite_prompt or fallback to config
                effective_rewrite_prompt = rewrite_prompt if rewrite_prompt is not None else self.config.rewrite_prompt
                # Rewrite transcript using AI
                rewritten_text = self.transcript_processor.rewrite_transcript(transcript, prompt=effective_rewrite_prompt)
                logger.info("Transcript rewritten by AI.")
                
                # Save rewritten transcript
                with open(output_dir / "rewritten_transcript.txt", "w", encoding="utf-8") as f:
                    f.write(rewritten_text)
                logger.info("Rewritten transcript saved.")
                processed_text = rewritten_text
            else:
                logger.info("Transcript rewriting skipped.")
                # If not rewriting, use original transcript for subsequent steps
                with open(output_dir / "rewritten_transcript.txt", "w", encoding="utf-8") as f:
                    f.write(transcript) # Still save original as rewritten for consistency
                logger.info("Original transcript used as rewritten transcript.")
            
            # Extract keywords and search for images
            keywords = self.transcript_processor.extract_keywords(processed_text)
            logger.info(f"Extracted keywords: {keywords}")
            
            # Calculate number of images needed
            logger.debug(f"Before image calculation: duration type: {type(duration)}, value: {duration}")
            logger.debug(f"Before image calculation: effective_seconds_per_image type: {type(effective_seconds_per_image)}, value: {effective_seconds_per_image}")
            images_needed = max(1, duration // effective_seconds_per_image)
            logger.info(f"Calculated images needed: {images_needed} (based on {duration}s duration and {effective_seconds_per_image}s per image)")
            
            # Search and download images/videos
            image_dir = output_dir / "images"
            downloaded_images, downloaded_videos = (0, 0) # Initialize
            if download_images or download_pexels_videos:
                downloaded_images, downloaded_videos = self.image_searcher.search_and_download(
                    keywords,
                    image_dir,
                    num_images_needed=images_needed if download_images else 0,
                    num_videos_needed=num_pexels_videos if download_pexels_videos else 0
                )
                logger.info(f"Image/Video search and download completed. Downloaded {downloaded_images} images and {downloaded_videos} videos.")
            else:
                logger.info("Image and Pexels video download skipped.")
            
            if generate_voiceover:
                # Generate voiceover
                audio_path = output_dir / "voiceover.wav"
                self.voice_generator.generate_audio(processed_text, audio_path)
                logger.info("Voiceover generated.")
            else:
                logger.info("Voiceover generation skipped.")
            
            logger.info(f"Successfully completed processing for video: {title} (ID: {video_id})")
            return transcript, processed_text # Return original and rewritten/processed transcript
            
        except Exception as e:
            logger.error(f"Error processing {title} (ID: {video_id}): {str(e)}", exc_info=True)
            return None, None # Return None if processing fails

def remove_pycache_dirs(base_path="."):
    """Removes all __pycache__ directories within the given base_path."""
    logger.info(f"Searching for and removing __pycache__ directories in {base_path}...")
    for root, dirs, files in os.walk(base_path):
        if "__pycache__" in dirs:
            pycache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(pycache_path)
                logger.info(f"Removed: {pycache_path}")
            except OSError as e:
                logger.warning(f"Error removing {pycache_path}: {e}")

if __name__ == "__main__":
    # Remove __pycache__ directories at the start
    remove_pycache_dirs()

    processor = VideoProcessor()
    
    try:
        logger.info("YouTube Video Processing Pipeline started.")
        logger.info("1. Process Channel")
        logger.info("2. Process Search Results")
        
        choice = input("Enter your choice (1 or 2): ").strip()
        
        if choice == "1":
            channel_url = input("Enter YouTube channel URL: ")
            max_videos = input("Enter max videos to process (or press Enter for all): ")
            max_videos = int(max_videos) if max_videos.strip() else None
            processor.process_channel(channel_url, max_videos)
            
        elif choice == "2":
            search_query = input("Enter search query: ")
            max_videos = input("Enter max videos to process (default 50): ")
            max_videos = int(max_videos) if max_videos.strip() else 50
            processor.process_search_results(search_query, max_videos)
            
        else:
            logger.warning("Invalid choice entered. Exiting.")
            
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
    except Exception as e:
        logger.critical(f"An unhandled critical error occurred: {str(e)}", exc_info=True)
    finally:
        if not processor.config.keep_browser_open:
            processor.close()
        else:
            logger.info("Selenium browser kept open for debugging as per configuration.")
            input("Press Enter to close the browser and exit the script...") # Keep browser open
        logger.info("YouTube Video Processing Pipeline finished.")
