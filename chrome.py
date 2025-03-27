import re
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from youtube_transcript_api.formatters import TextFormatter

# Variables
search_query = "plus size model instagram"  # Set your search query
scroll_limit = 10  # Number of scrolls to perform
formatted_query = search_query.replace(" ", "_")  # Format query for filename
filename = f"{datetime.now().strftime('%Y-%m-%d')}_{formatted_query}.csv"  # Dynamic filename

# Set up the ChromeDriver
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Open the YouTube URL with the search query
url = f"https://youtube.com/results?search_query={search_query.replace(' ', '+')}&sp=CAMSAggD"
driver.get(url)

# Scroll a limited number of times
for _ in range(scroll_limit):
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(2)  # Adjust pause time if needed

# Extract video details
videos = driver.find_elements(By.XPATH, '//*[@id="video-title"]')

# Prepare CSV file
existing_video_ids = set()

try:
    with open(filename, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            existing_video_ids.add(row[0])
except FileNotFoundError:
    pass

formatter = TextFormatter()
with open(filename, 'a', newline='') as file:
    writer = csv.writer(file)

    for video in videos:
        href = video.get_attribute("href")
        title = video.get_attribute("title")

        if href and title and "/shorts/" not in href:
            video_id = href.split("?v=")[1].split("&")[0]
            video_url = href

            if video_id not in existing_video_ids:
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id)
                    formatted_text = formatter.format_transcript(transcript)
                    formatted_text = re.sub(r'\n(?!\n)|\[Music\]', ' ', formatted_text)
                    writer.writerow([video_id, title, video_url, formatted_text])
                    print(f"+++ Transcript SAVED for {video_id}")
                except TranscriptsDisabled:
                    print(f"--- Transcript DISABLED for {video_id}")
                except NoTranscriptFound:
                    print(f"--- No transcript found for {video_id}")
                except Exception as e:
                    print(f"--- Error for {video_id}: {str(e)}")
            else:
                print(f"Duplicate video ID found: {video_id}")

# Close the browser
driver.quit()
