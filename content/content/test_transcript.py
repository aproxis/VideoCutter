import sys
import os
from pathlib import Path
import re

# Add the content directory to the Python path
sys.path.append(str(Path(__file__).parent / "content"))

from youtube_handler import YouTubeHandler
from config import Config

def test_transcript_function(video_id):
    print(f"Testing transcript for video ID: {video_id}")
    
    # Initialize Config (assuming config.json exists in the content/ directory)
    config = Config("content/config.json")
    
    # Initialize YouTubeHandler
    # Note: YouTubeHandler's search_videos and get_channel_videos methods
    # now fetch transcripts and log them to CSV.
    # For direct transcript retrieval, we'll simulate a search for a single video.
    handler = YouTubeHandler(config)

    try:
        # Since get_transcript is deprecated, we'll simulate a search for this video ID
        # This is a workaround for testing the transcript fetching logic directly
        # without running the full search/channel logic.
        # In a real scenario, main.py would call search_videos or get_channel_videos
        # which would then populate the video_info with the transcript.
        
        # For testing, we'll manually call the underlying YouTubeTranscriptApi
        # as the main purpose is to test the transcript fetching logic itself.
        # However, to demonstrate the *integrated* functionality as per the new design,
        # we should ideally call search_videos and then extract the transcript.
        # Let's try to simulate a search for a very specific query that would return this video.
        # This might be tricky, so a direct call to YouTubeTranscriptApi is simpler for isolated testing.
        
        # Re-reading the youtube_handler.py, the get_transcript method is still there,
        # but it's marked as deprecated and returns None.
        # The transcripts are now fetched within search_videos and get_channel_videos.
        # So, to test the *new* way, we need to call one of those.
        # Let's make a dummy call to search_videos with a very specific query
        # that should ideally return this video, and then extract its transcript.
        
        # A more direct way to test the transcript API part, without Selenium overhead:
        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
        from youtube_transcript_api.formatters import TextFormatter
        
        formatter = TextFormatter()
        
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])
            formatted_text = formatter.format_transcript(transcript_list)
            # Apply the same cleaning regex as in youtube_handler.py
            formatted_text = re.sub(r'\n(?!\n)|\[Music\]|\[Applause\]|\[Laughter\]', ' ', formatted_text)
            formatted_text = re.sub(r'\s+', ' ', formatted_text).strip()
            
            print("\n--- Fetched Transcript ---")
            print(formatted_text)
            print("--------------------------")
            
        except TranscriptsDisabled:
            print(f"--- Transcript DISABLED for {video_id} ---")
        except NoTranscriptFound:
            print(f"--- No transcript found for {video_id} ---")
        except Exception as e:
            print(f"--- Error getting transcript for {video_id}: {str(e)} ---")
            
    finally:
        handler.close() # Ensure Selenium driver is closed

if __name__ == "__main__":
    # Extract video ID from the provided URL
    video_url = "https://www.youtube.com/watch?v=TkeZLyi7ziQ"
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(video_url)
    video_id = parse_qs(parsed_url.query).get('v', [None])[0]

    if video_id:
        test_transcript_function(video_id)
    else:
        print("Invalid YouTube URL provided.")
