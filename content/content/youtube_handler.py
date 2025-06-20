# youtube_handler.py - YouTube handling via Selenium only
import re
import os
import csv
import time
import json # Added for JSON parsing
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait # Added for explicit waits
from selenium.webdriver.support import expected_conditions as EC # Added for explicit waits
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from PIL import Image # Added for image processing
from io import BytesIO # Added for image processing
import requests # Added for downloading images
from PyQt5.QtGui import QPixmap, QImage # Added for GUI thumbnail display
import urllib.parse # Added for URL parsing

logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)

class YouTubeHandler:
    def __init__(self, config):
        self.config = config
        logger.info("Initializing YouTubeHandler...")
        self.setup_selenium()
        self.ytt_api = YouTubeTranscriptApi()
        logger.info("YouTubeHandler initialized.")
    
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        logger.info("Setting up Selenium WebDriver...")
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        if self.config.headless_browser:
            options.add_argument("--headless")
            logger.info("Running browser in headless mode.")
            
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Selenium WebDriver setup complete.")
        except Exception as e:
            logger.error(f"Failed to set up Selenium WebDriver: {str(e)}", exc_info=True)
            raise
    
    def search_videos(self, search_query, output_base_dir, max_videos=50, youtube_filter=""):
        """Search for videos using Selenium"""
        logger.info(f"Searching YouTube with Selenium: '{search_query}' (max_videos: {max_videos}, youtube_filter: '{youtube_filter}')")
        
        url = f"https://youtube.com/results?search_query={search_query.replace(' ', '+')}{youtube_filter}"
        logger.info(f"Navigating to search URL: {url}")
        self.driver.get(url)
        
        scroll_limit = min(10, max_videos // 20)
        logger.info(f"Scrolling to load more videos (scroll_limit: {scroll_limit})...")
        for i in range(scroll_limit):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2) # Adjust pause time if needed
            logger.debug(f"Scrolled {i+1}/{scroll_limit} times.")
        
        videos_info = [] # To store video info
        time.sleep(3) # Adjust pause time if needed

        video_elements = self.driver.find_elements(By.XPATH, '//ytd-video-renderer//a[@id="video-title"]')
        # Try to extract from ytInitialData first
        yt_initial_data = self._extract_yt_initial_data()
        if yt_initial_data:
            videos_info = self._parse_video_data_from_yt_initial_data(yt_initial_data, is_channel_page=False)
            if videos_info:
                logger.info(f"Extracted {len(videos_info)} videos from ytInitialData for search results.")
                return videos_info[:max_videos], None # Limit to max_videos
        
        logger.info("Falling back to Selenium scraping for search results...")
        video_elements = self.driver.find_elements(By.XPATH, '//ytd-video-renderer//a[@id="video-title"]')
        logger.info(f"Found {len(video_elements)} video elements on the page.")
        
        for i, video_element in enumerate(video_elements[:max_videos]):
            href = video_element.get_attribute("href")
            title = video_element.get_attribute("title")
            
            if href and title and "/shorts/" not in href:
                video_id = href.split("?v=")[1].split("&")[0]
                video_url = href
                
                # Check for PREMIERE/UPCOMING badges
                if self._is_special_video(video_element):
                    logger.info(f"--- Skipping video {video_id} ('{title}') due to PREMIERE/UPCOMING status.")
                    continue

                logger.debug(f"Processing video element {i+1}: ID={video_id}, Title='{title}'")

                duration = self._estimate_duration_selenium(video_element)
                
                videos_info.append({
                    'id': video_id,
                    'title': title,
                    'url': video_url,
                    'duration': duration,
                    'published_at': None,
                    'description': '',
                    'thumbnail_url': self._get_thumbnail_url_from_element(video_element) # Get thumbnail from element
                })
            else:
                logger.debug(f"Skipping video element {i+1} (no href/title or is a short).")
        
        logger.info(f"Finished searching videos. Found {len(videos_info)} videos matching criteria.")
        return videos_info, None # No CSV file is written here anymore
    
    def get_channel_videos(self, channel_url, output_base_dir, max_videos=None):
        """Get videos from channel using Selenium"""
        logger.info(f"Getting channel videos with Selenium: '{channel_url}' (max_videos: {max_videos})")
        
        logger.info(f"Navigating to channel videos URL: {channel_url}/videos")
        self.driver.get(channel_url + "/videos")
        time.sleep(3)
        
        # Try to extract from ytInitialData first
        yt_initial_data = self._extract_yt_initial_data()
        if yt_initial_data:
            videos_info = self._parse_video_data_from_yt_initial_data(yt_initial_data, is_channel_page=True)
            if videos_info:
                logger.info(f"Extracted {len(videos_info)} videos from ytInitialData for channel.")
                return videos_info[:max_videos] if max_videos else videos_info, None
        
        logger.info("Falling back to Selenium scraping for channel videos...")
        scroll_limit = min(15, (max_videos or 100) // 20)
        logger.info(f"Scrolling to load more videos (scroll_limit: {scroll_limit})...")
        for i in range(scroll_limit):
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            logger.debug(f"Scrolled {i+1}/{scroll_limit} times.")
        
        videos_info = [] # To store video info
        video_links = self.driver.find_elements(By.XPATH, '//a[@id="video-title-link" and contains(@href, "/watch")]')
        

        logger.info(f"Found {len(video_links)} video links on the page.")
        
        for i, link in enumerate(video_links[:max_videos] if max_videos else video_links):
            href = link.get_attribute("href")
            title = link.get_attribute("title")
            
            if href and title:
                video_id_match = re.search(r'watch\?v=([^&]+)', href)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    video_url = href

                    # Check for PREMIERE/UPCOMING badges
                    if self._is_special_video(link): # Pass the link element to check for badges
                        logger.info(f"--- Skipping video {video_id} ('{title}') due to PREMIERE/UPCOMING status.")
                        continue

                    logger.debug(f"Processing video link {i+1}: ID={video_id}, Title='{title}'")

                    duration = self._estimate_duration_selenium(link) # Re-using the method, might need adjustment for channel page elements
                    
                    videos_info.append({
                        'id': video_id,
                        'title': title,
                        'url': video_url,
                        'duration': duration,
                        'published_at': None,
                        'description': '',
                        'thumbnail_url': self._get_thumbnail_url_from_element(link) # Get thumbnail from element
                    })
            else:
                logger.debug(f"Skipping video link {i+1} (no href/title).")
        
        logger.info(f"Finished getting channel videos. Found {len(videos_info)} videos matching criteria.")
        return videos_info, None # No CSV file is written here anymore

    def get_video_info_from_url(self, video_url):
        """Get video information from a single YouTube video URL, handling search result URLs."""
        logger.info(f"Getting video info for single URL: {video_url}")
        video_id = None
        try:
            # Check if it's a YouTube search results URL
            if "youtube.com/results?search_query=" in video_url:
                parsed_url = urllib.parse.urlparse(video_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                if 'search_query' in query_params and query_params['search_query']:
                    video_id = query_params['search_query'][0]
                    logger.info(f"Extracted video ID '{video_id}' from search results URL.")
                else:
                    logger.error(f"Could not extract video ID from search results URL: {video_url}")
                    return None
            else:
                # Standard video ID extraction from watch?v= or youtu.be/
                video_id_match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:&|\?|$)', video_url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    logger.info(f"Extracted video ID '{video_id}' from standard video URL.")
                else:
                    logger.error(f"Could not extract video ID from URL: {video_url}")
                    return None

            # If video_id is successfully extracted, proceed to get video details
            if video_id:
                # Navigate to the video page to get title and duration
                self.driver.get(f"https://www.youtube.com/watch?v={video_id}")
                time.sleep(3) # Give page time to load for ytInitialData to load

                # Attempt to extract video info from ytInitialData first (more robust)
                yt_initial_data = self._extract_yt_initial_data()
                if yt_initial_data:
                    parsed_video_info = self._parse_single_video_data_from_yt_initial_data(yt_initial_data)
                    if parsed_video_info and parsed_video_info.get('id') == video_id:
                        logger.info(f"Extracted video info from ytInitialData (single page): {parsed_video_info.get('title')} (ID: {video_id})")
                        # Update duration using Selenium if not available from ytInitialData
                        if parsed_video_info.get('duration') == 0:
                            parsed_video_info['duration'] = self._estimate_duration_selenium(self.driver.find_element(By.TAG_NAME, 'body'))
                        return parsed_video_info
                    else:
                        logger.warning("ytInitialData parsing for single video failed or returned wrong video. Falling back to Selenium element finding.")

                # Fallback to Selenium element finding with explicit waits
                wait = WebDriverWait(self.driver, 10) # Wait up to 10 seconds

                # Try common title XPaths
                title_element = None
                try:
                    title_element = wait.until(EC.presence_of_element_located((By.XPATH, '//h1/yt-formatted-string')))
                except:
                    try:
                        title_element = wait.until(EC.presence_of_element_located((By.XPATH, '//h1[@class="style-scope ytd-watch-metadata"]/yt-formatted-string')))
                    except:
                        logger.warning("Could not find title element using common XPaths.")
                        pass # Will be handled by title check below

                title = title_element.text.strip() if title_element else "Unknown Title"
                
                duration = self._estimate_duration_selenium(self.driver.find_element(By.TAG_NAME, 'body')) # Pass body to estimate duration from anywhere on page

                video_info = {
                    'id': video_id,
                    'title': title,
                    'url': f"https://www.youtube.com/watch?v={video_id}", # Ensure canonical URL
                    'duration': duration,
                    'published_at': None, # Not easily available via Selenium on single page
                    'description': '', # Not easily available via Selenium on single page
                    'thumbnail_url': '' # Not easily available via Selenium on single page
                }
                logger.info(f"Found video: {title} (ID: {video_id}, Duration: {duration}s)")
                return video_info
            else:
                return None # Should not happen if previous checks are correct

        except Exception as e:
            logger.error(f"Error getting video info for {video_url}: {str(e)}", exc_info=True)
            return None

    def _get_thumbnail_url_from_element(self, video_element):
        """Extracts the thumbnail URL from a Selenium video element."""
        try:
            # Look for img tag within the thumbnail container
            img_element = video_element.find_element(By.XPATH, './/img[contains(@src, "ytimg.com/vi/")]')
            full_thumbnail_url = img_element.get_attribute('src')
            return full_thumbnail_url.split('?')[0] # Strip query parameters
        except Exception as e:
            logger.debug(f"Could not extract thumbnail URL from element: {e}")
            return ""

    def _estimate_duration_selenium(self, video_element):
        """Estimate video duration from Selenium element"""
        duration_text = None
        try:
            # Attempt 1: Find duration for channel video links (yt-formatted-string with id="length")
            # The video_element here is typically the <a> tag for the video title.
            # We need to find the duration element relative to it.
            
            # Find the common ancestor that contains both the video link and the duration element
            # This XPath looks for ytd-rich-item-renderer, ytd-grid-video-renderer, or ytd-video-renderer
            # which are common containers for video elements.
            ancestor_container = None
            try:
                ancestor_container = video_element.find_element(By.XPATH, "./ancestor::ytd-rich-item-renderer[1] | ./ancestor::ytd-grid-video-renderer[1] | ./ancestor::ytd-video-renderer[1]")
            except:
                pass # If not found, ancestor_container remains None

            if ancestor_container:
                try:
                    # Search for the duration element within the identified ancestor container
                    duration_element = ancestor_container.find_element(By.XPATH, './/yt-formatted-string[@id="length"]')
                    duration_text = duration_element.text.strip()
                except:
                    pass # Fall through to other methods if not found within ancestor

            if not duration_text:
                # Attempt 2: Fallback to JavaScript for search results or other structures
                duration_text = self.driver.execute_script("""
                    const videoElement = arguments[0];
                    const timeStatusRenderer = videoElement.closest('ytd-video-renderer, ytd-grid-video-renderer')
                                                ?.querySelector('span.ytd-thumbnail-overlay-time-status-renderer');
                    return timeStatusRenderer?.textContent.trim();
                """, video_element)
            
            if not duration_text:
                # Attempt 3: Fallback to XPath for search results if JavaScript fails
                try:
                    ancestor_video_renderer = video_element.find_element(By.XPATH, "./ancestor::ytd-video-renderer[1] | ./ancestor::ytd-grid-video-renderer[1]")
                    duration_element = ancestor_video_renderer.find_element(
                        By.XPATH, ".//ytd-thumbnail-overlay-time-status-renderer span"
                    )
                    duration_text = duration_element.text.strip()
                except:
                    pass

            if duration_text:
                logger.debug(f"Estimated duration text (before parsing): '{duration_text}'")
                parsed_duration = self._parse_duration_text(duration_text)
                logger.debug(f"Parsed duration (from _estimate_duration_selenium): {parsed_duration}")
                return parsed_duration
            else:
                raise ValueError("Duration text not found by any method.")
        
        except Exception as e:
            logger.warning(f"Could not estimate duration from Selenium element: {str(e)}. Defaulting to 300s.", exc_info=True)
            return 300
        except Exception as e:
            logger.warning(f"Could not estimate duration from Selenium element: {str(e)}. Defaulting to 300s.", exc_info=True)
            return 300

    def _extract_yt_initial_data(self):
        """Extracts and parses ytInitialData from the current page source."""
        script_tags = self.driver.find_elements(By.TAG_NAME, 'script')
        for script_tag in script_tags:
            script_content = script_tag.get_attribute('innerHTML')
            if script_content and 'var ytInitialData =' in script_content:
                try:
                    # Use regex to find the JSON object more precisely
                    # It looks for 'var ytInitialData = ' followed by a JSON object
                    # and captures the JSON content. It handles cases where there's a semicolon
                    # or other JS code immediately after the JSON.
                    match = re.search(r'var ytInitialData = ({.*?});', script_content, re.DOTALL)
                    if not match:
                        # Fallback if the first regex doesn't find it (e.g., no semicolon)
                        match = re.search(r'var ytInitialData = ({.*})', script_content, re.DOTALL)
                    
                    if match:
                        json_str = match.group(1)
                        return json.loads(json_str)
                    else:
                        logger.warning("Could not find ytInitialData JSON pattern in script content.")
                except Exception as e:
                    logger.warning(f"Failed to parse ytInitialData: {e}")
        return None

    def _parse_video_data_from_yt_initial_data(self, yt_initial_data, is_channel_page=False):
        """
        Parses video data from ytInitialData JSON structure.
        Handles both search results and channel video pages.
        """
        videos_info = []
        try:
            if is_channel_page:
                # Path for channel videos tab
                contents = yt_initial_data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
                for tab in contents:
                    if tab.get('tabRenderer', {}).get('selected') and tab.get('tabRenderer', {}).get('title') == 'Videos':
                        grid_contents = tab.get('tabRenderer', {}).get('content', {}).get('richGridRenderer', {}).get('contents', [])
                        break
                else:
                    logger.warning("Could not find selected 'Videos' tab in ytInitialData for channel.")
                    return []
            else:
                # Path for search results
                grid_contents = yt_initial_data.get('contents', {}).get('twoColumnSearchResultsRenderer', {}).get('primaryContents', {}).get('sectionListRenderer', {}).get('contents', [])
                # Search results can have multiple sections, find the one with video renderers
                for section in grid_contents:
                    if 'itemSectionRenderer' in section:
                        grid_contents = section['itemSectionRenderer'].get('contents', [])
                        break
                else:
                    logger.warning("Could not find video section in ytInitialData for search results.")
                    return []

            for item in grid_contents:
                if 'richItemRenderer' in item:
                    video_data = item['richItemRenderer'].get('content', {}).get('videoRenderer', {})
                elif 'videoRenderer' in item: # For some search result structures
                    video_data = item['videoRenderer']
                else:
                    continue # Skip non-video items or continuations

                if not video_data:
                    continue

                video_id = video_data.get('videoId')
                title = video_data.get('title', {}).get('simpleText') or video_data.get('title', {}).get('runs', [{}])[0].get('text')
                
                # Extract duration
                duration_text = video_data.get('lengthText', {}).get('simpleText')
                duration = self._parse_duration_text(duration_text) if duration_text else 0

                # Extract thumbnail URL (get the largest available) and clean it
                thumbnail_url = ''
                thumbnails = video_data.get('thumbnail', {}).get('thumbnails', [])
                if thumbnails:
                    full_thumbnail_url = thumbnails[-1].get('url', '') # Get the last (largest) thumbnail
                    thumbnail_url = full_thumbnail_url.split('?')[0] # Strip query parameters

                # Check for PREMIERE/UPCOMING badges from JSON structure
                is_special = False
                if 'thumbnailOverlays' in video_data:
                    for overlay in video_data['thumbnailOverlays']:
                        if 'thumbnailOverlayTimeStatusRenderer' in overlay:
                            overlay_text = overlay['thumbnailOverlayTimeStatusRenderer'].get('text', {}).get('simpleText', '').upper()
                            if overlay_text in ["PREMIERE", "UPCOMING"]:
                                is_special = True
                                break
                
                if is_special:
                    logger.info(f"--- Skipping video {video_id} ('{title}') due to PREMIERE/UPCOMING status (from ytInitialData).")
                    continue

                if video_id and title and duration is not None:
                    videos_info.append({
                        'id': video_id,
                        'title': title,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'duration': duration,
                        'published_at': None, # Not easily available here
                        'description': '', # Not easily available here
                        'thumbnail_url': thumbnail_url # Add thumbnail URL
                    })

        except Exception as e:
            logger.warning(f"Error parsing video data from ytInitialData: {e}", exc_info=True)
        return videos_info

    def _parse_single_video_data_from_yt_initial_data(self, yt_initial_data):
        """
        Parses video data from ytInitialData JSON structure for a single video page.
        """
        video_info = {}
        try:
            # Path for single video page
            # This path can be complex and may vary. Common paths include:
            # contents.twoColumnWatchNextResults.results.results.contents[0].videoPrimaryInfoRenderer
            # contents.twoColumnWatchNextResults.results.results.contents[1].videoSecondaryInfoRenderer
            
            # Try to find primary info renderer
            primary_info = yt_initial_data.get('contents', {}).get('twoColumnWatchNextResults', {}).get('results', {}).get('results', {}).get('contents', [{}])[0].get('videoPrimaryInfoRenderer', {})
            
            if primary_info:
                video_id = primary_info.get('videoActions', {}).get('menuRenderer', {}).get('topLevelButtons', [{}])[0].get('segmentedLikeDislikeButtonRenderer', {}).get('likeButton', {}).get('toggleButtonRenderer', {}).get('defaultServiceEndpoint', {}).get('commandMetadata', {}).get('webCommandMetadata', {}).get('url', '').split('v=')[-1]
                title = primary_info.get('title', {}).get('runs', [{}])[0].get('text')
                
                # Duration is not typically in primaryInfoRenderer for single video page
                # It's usually in secondary info or needs to be scraped from the player
                # For now, we'll rely on _estimate_duration_selenium for duration if not found here.
                
                # Thumbnail is also not typically in ytInitialData for single video page,
                # as the page is already displaying the video.
                
                if video_id and title:
                    video_info = {
                        'id': video_id,
                        'title': title,
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'duration': 0, # Will be updated by _estimate_duration_selenium
                        'published_at': None,
                        'description': '',
                        'thumbnail_url': '' # Not easily available here
                    }
                    logger.info(f"Extracted video info from ytInitialData (single page): {title} (ID: {video_id})")
            else:
                logger.warning("Could not find videoPrimaryInfoRenderer in ytInitialData for single video page.")

        except Exception as e:
            logger.warning(f"Error parsing single video data from ytInitialData: {e}", exc_info=True)
        return video_info

    def _is_special_video(self, video_element):
        """Checks if a video element has PREMIERE or UPCOMING badges."""
        try:
            # Try to find the badge text within the video element's context
            # This XPath looks for the badge text within the common overlay structure
            badge_elements = video_element.find_elements(By.XPATH, './/ytd-thumbnail-overlay-time-status-renderer/div[1]/badge-shape/div[contains(@class, "badge-shape-wiz__text")]')
            
            for badge_element in badge_elements:
                badge_text = badge_element.text.strip().upper()
                if badge_text in ["PREMIERE", "UPCOMING"]:
                    return True
            return False
        except Exception as e:
            logger.debug(f"Could not check for special video badges: {str(e)}")
            return False # Assume not special if check fails

    def _parse_duration_text(self, duration_text):
        """Convert duration string like '5:30' to seconds"""
        logger.debug(f"Attempting to parse duration text: '{duration_text}'")
        try:
            parts = duration_text.strip().split(':')
            if len(parts) == 2:
                seconds = int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3:
                seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            else:
                raise ValueError(f"Invalid duration format: '{duration_text}'")
            logger.debug(f"Parsed duration '{duration_text}' to {seconds} seconds.")
            return seconds
        except Exception as e:
            logger.warning(f"Could not parse duration text '{duration_text}': {str(e)}. Defaulting to 300s.", exc_info=True)
            return 300

    def fetch_transcript_for_video(self, video_id):
        """Fetches the transcript for a given video ID using youtube-transcript-api."""
        try:
            logger.info(f"Attempting to get transcript for {video_id}...")
            fetched_transcript = self.ytt_api.fetch(video_id, languages=['en', 'en-US', 'en-GB'])
            formatted_text = " ".join([snippet['text'] for snippet in fetched_transcript.to_raw_data()])
            # Clean up transcript
            formatted_text = re.sub(r'\[Music\]|\[Applause\]|\[Laughter\]', '', formatted_text) # Remove specific tags
            formatted_text = re.sub(r'\s+', ' ', formatted_text).strip() # Replace multiple spaces/newlines with single space
            logger.info(f"Transcript fetched for {video_id}. Length: {len(formatted_text)} characters.")
            return formatted_text
        except TranscriptsDisabled:
            logger.warning(f"--- Transcript DISABLED for {video_id}")
            return None
        except NoTranscriptFound:
            logger.warning(f"--- No transcript found for {video_id}")
            return None
        except Exception as e:
            logger.error(f"--- Error getting transcript for {video_id}: {str(e)}", exc_info=True)
            return None

    def close(self):
        """Close the browser"""
        logger.info("Closing Selenium WebDriver...")
        if hasattr(self, 'driver'):
            self.driver.quit() # Commented out for debugging purposes
            logger.info("Selenium WebDriver closed.")
        else:
            logger.info("No Selenium WebDriver to close.")
