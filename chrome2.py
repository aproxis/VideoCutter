import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# Set up the ChromeDriver
options = Options()
# options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)
driver = webdriver.Chrome(options=options)

# Open the YouTube URL with the search query and sp parameter
url = "https://www.youtube.com/results?search_query=plus+size+instagram+model&sp=CAMSAggD"
driver.get(url)

# Wait for the page to load
time.sleep(2)

# Find all video elements using the specified XPath
videos = driver.find_elements(By.ID, 'video-title')

# Create a list to store video information
video_info = []

# Iterate through the video elements and extract video IDs, titles, and URLs
for video in videos:
    href_attribute = video.get_attribute("href")
    video_title = video.get_attribute("title")

    if href_attribute and video_title and "/shorts/" not in href_attribute:
        parts = href_attribute.split("?v=")
        if len(parts) >= 2:
            video_id = parts[1].split("&")[0]
            video_info.append({"ID": video_id, "Title": video_title, "URL": "https://www.youtube.com" + href_attribute})

# Initialize a TextFormatter
formatter = TextFormatter()

# Open a text file to save all the results
with open('video_results.txt', 'w', encoding='utf-8') as result_file:
    # Process and save the transcript for each video
    for video in video_info:
        video_id = video["ID"]
        video_title = video["Title"]
        video_url = video["URL"]

        try:
            # Get the transcript
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print(transcript_list)
            srt = transcript_list.find_manually_created_transcript(['en'])
            if srt is None:
                srt = transcript_list.find_generated_transcript(['en'])

            # Format the transcript
            text_formatted = formatter.format_transcript(srt)

            # Replace single line breaks and [Music] with spaces
            text_formatted = re.sub(r'\n(?!\n)|\[Music\]', ' ', text_formatted)


            # Write the results for each video to the file
            result_file.write(f"Video ID: {video_id}\n")
            result_file.write(f"Video Title: {video_title}\n")
            result_file.write(f"Video URL: {video_url}\n")
            result_file.write("Video Transcript:\n")
            result_file.write(f"{text_formatted}\n\n")

            print(f"Transcript for video ID {video_id} saved.")
        except TranscriptsDisabled:
            print(f"Transcripts are disabled for video ID {video_id}. Skipping.")
        except NoTranscriptFound:
            print(f"No transcript found for video ID {video_id}. Skipping.")

# Close the browser window
driver.quit()
