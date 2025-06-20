import requests
import os
import logging
from pathlib import Path
import time

logger = logging.getLogger(__name__)

class ImageSearcher:
    def __init__(self, config):
        self.config = config
        self.api_key = config.pexels_api_key
        self.image_base_url = 'https://api.pexels.com/v1/'
        self.video_base_url = 'https://api.pexels.com/videos/'
        self._pexels_auto_approve = False # Flag for "yes to all"
        logger.info("ImageSearcher initialized.")

    def search_images(self, query, per_page=15):
        """Search for images on Pexels"""
        logger.info(f"Searching Pexels for images with query: '{query}' (per_page: {per_page})")
        headers = {'Authorization': self.api_key}
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'landscape'
        }
        try:
            response = requests.get(self.image_base_url + 'search', headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                image_urls = [photo['src']['original'] for photo in data['photos']]
                logger.info(f"Found {len(image_urls)} images for query '{query}'.")
                return image_urls
            else:
                logger.error(f'Error searching images for "{query}": {response.status_code} - {response.text}')
                return []
        except Exception as e:
            logger.error(f"Exception during image search for '{query}': {str(e)}", exc_info=True)
            return []

    def search_videos(self, query, per_page=10):
        """Search for videos on Pexels"""
        logger.info(f"Searching Pexels for videos with query: '{query}' (per_page: {per_page})")
        headers = {'Authorization': self.api_key}
        params = {
            'query': query,
            'per_page': per_page
        }
        try:
            response = requests.get(self.video_base_url + 'search', headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                video_urls = [video['video_files'][0]['link'] for video in data['videos'] if video['video_files']]
                logger.info(f"Found {len(video_urls)} videos for query '{query}'.")
                return video_urls
            else:
                logger.error(f'Error searching videos for "{query}": {response.status_code} - {response.text}')
                return []
        except Exception as e:
            logger.error(f"Exception during video search for '{query}': {str(e)}", exc_info=True)
            return []

    def save_media(self, media_urls, query, save_directory, media_type='image'):
        """Save media (image or video) from URLs to directory"""
        logger.info(f"Attempting to save {len(media_urls)} {media_type}s to {save_directory} for query '{query}'.")
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
            logger.info(f"Created directory: {save_directory}")

        saved_count = 0
        ext = '.jpg' if media_type == 'image' else '.mp4'

        for i, url in enumerate(media_urls):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    file_path = os.path.join(save_directory, f'{safe_query}_{media_type}_{i+1}{ext}')
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f'Saved: {file_path}')
                    saved_count += 1
                else:
                    logger.warning(f'Error downloading {media_type} {i+1} from {url}: {response.status_code} - {response.text}')
                time.sleep(0.3) # Rate limiting
            except Exception as e:
                logger.error(f'Exception downloading {media_type} {i+1} from {url}: {str(e)}', exc_info=True)

        logger.info(f"Finished saving media. Saved {saved_count} {media_type}s.")
        return saved_count

    def search_and_download(self, keywords, output_dir, num_images_needed=0, num_videos_needed=0):
        """Search and download both images and videos based on specified counts."""
        logger.info(f"Starting media download for keywords: {keywords}")
        logger.info(f"Target: {num_images_needed} images, {num_videos_needed} videos.")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Output directory for media: {output_dir}")

        downloaded_images = 0
        downloaded_videos = 0

        # Use configurable limit for images per keyword
        images_per_keyword_limit = self.config.images_per_keyword_limit
        # Videos per keyword can still be dynamically calculated or set to a default
        videos_per_keyword = max(1, num_videos_needed // len(keywords)) if keywords else 1

        for keyword in keywords:
            logger.info(f"Processing keyword: '{keyword}'")
            
            # --- Image Download Logic ---
            if num_images_needed > 0 and downloaded_images < num_images_needed:
                logger.info(f"Pexels search for images with keyword '{keyword}' will request up to {images_per_keyword_limit} results.")
                remaining_images = num_images_needed - downloaded_images
                image_urls = self.search_images(keyword, per_page=images_per_keyword_limit + 2) # Request a few extra
                image_urls_to_download = image_urls[:min(images_per_keyword_limit, remaining_images)]
                logger.info(f"Found {len(image_urls)} images for '{keyword}'. Will attempt to download {len(image_urls_to_download)}.")
                downloaded_images += self.save_media(image_urls_to_download, keyword, str(output_dir), media_type='image')
            else:
                logger.info(f"Skipping image search for '{keyword}'. Target reached or no images needed.")

            # --- Video Download Logic ---
            if num_videos_needed > 0 and downloaded_videos < num_videos_needed:
                logger.info(f"Pexels search for videos with keyword '{keyword}' will request up to {videos_per_keyword} results.")
                remaining_videos = num_videos_needed - downloaded_videos
                video_urls = self.search_videos(keyword, per_page=videos_per_keyword + 2) # Request a few extra
                video_urls_to_download = video_urls[:min(videos_per_keyword, remaining_videos)]
                logger.info(f"Found {len(video_urls)} videos for '{keyword}'. Will attempt to download {len(video_urls_to_download)}.")
                downloaded_videos += self.save_media(video_urls_to_download, keyword, str(output_dir), media_type='video')
            else:
                logger.info(f"Skipping video search for '{keyword}'. Target reached or no videos needed.")

        logger.info(f"Total downloaded: {downloaded_images} images, {downloaded_videos} videos.")
        return downloaded_images, downloaded_videos
