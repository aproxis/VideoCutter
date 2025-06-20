**File: `content/config.py`**

**Core Purpose and Logic:**
This script defines the `Config` class, which is responsible for managing the application's configuration settings. It handles loading configuration from a `config.json` file, creating a default configuration if the file doesn't exist, saving configuration changes, and providing access to various settings such as API keys, YouTube preferences, AI model parameters, image generation settings, text-to-speech (TTS) voice options, and output directory.

**Internal Dependencies:**
- None

**External Dependencies:**
- `json`: For reading from and writing to JSON configuration files.
- `os`: For checking file existence (`os.path.exists`).
- `pathlib.Path`: Imported but not directly used in the provided snippet.

**Inputs:**

**`Config` class constructor:**
- `config_path` (str, optional): The path to the configuration JSON file. Defaults to "config.json".

**`load_config` method:**
- Reads from the file specified by `self.config_path`.

**`save_config` method:**
- `config_data` (dict): A dictionary containing the configuration settings to be saved.

**`update_rewrite_prompt` method:**
- `new_prompt` (str): The new AI rewrite prompt string.

**Files (read by the script):**
- `config.json` (if it exists).

**Outputs:**

**`Config` class constructor:**
- Initializes instance attributes with configuration values.

**`load_config` method:**
- Populates instance attributes (`self.youtube_api_key`, `self.ai_model`, etc.) with loaded or default configuration values.
- Creates and saves a default `config.json` if it doesn't exist.

**`create_default_config` method:**
- Returns a dictionary representing the default configuration.

**`save_config` method:**
- Writes the provided `config_data` to the file specified by `self.config_path`.

**`update_rewrite_prompt` method:**
- Updates the `self.rewrite_prompt` attribute and saves the updated configuration to `config.json`.

**Files (written by the script):
- `config.json` (created if not exists, or updated).

---

**File: `content/image_searcher.py`**

**Core Purpose and Logic:**
This script defines the `ImageSearcher` class, which handles searching for and downloading images from the Pexels API. It provides methods to search for images based on a query, save image URLs to a local directory, and orchestrate the search and download process for a list of keywords, ensuring a specified number of images are downloaded and respecting API rate limits.

**Internal Dependencies:**
- `config.Config`: The `ImageSearcher` class depends on the `Config` object to retrieve the Pexels API key.

**External Dependencies:**
- `requests`: For making HTTP requests to the Pexels API and downloading images.
- `os`: For file system operations like creating directories and joining paths.
- `pathlib.Path`: For object-oriented path manipulation, specifically for creating output directories.
- `time`: For implementing rate limiting (`time.sleep`).

**Inputs:**

**`ImageSearcher` class constructor:**
- `config` (Config object): An instance of the `Config` class containing the `pexels_api_key`.

**`search` method:**
- `query` (str): The search term for images.
- `per_page` (int, optional): The number of results to request per page from the Pexels API. Defaults to 15.

**`save_images` method:**
- `image_urls` (list of str): A list of image URLs to download.
- `query` (str): The original search query, used for creating safe filenames.
- `save_directory` (str): The path to the directory where images will be saved.

**`search_and_download` method:**
- `keywords` (list of str): A list of keywords to search for images.
- `output_dir` (str): The base directory where images will be saved (subdirectories will be created for each keyword).
- `num_images_needed` (int): The total number of images required across all keywords.

**API Payloads (read by the script):**
- JSON responses from the Pexels API search endpoint.

**Outputs:**

**`search` method:**
- Returns a list of original image URLs if the search is successful, otherwise an empty list.
- Prints error messages to the console if the API request fails.

**`save_images` method:**
- Returns the count of successfully saved images.
- Creates directories if they don't exist.
- Writes image content to `.jpg` files in the specified directory.
- Prints messages indicating saved files or download errors.

**`search_and_download` method:**
- Returns the total count of downloaded images.
- Creates the `output_dir` if it doesn't exist.
- Orchestrates searching and downloading, distributing the `num_images_needed` across provided `keywords`.
- Prints progress and status messages to the console.

**Files (written by the script):**
- Image files (e.g., `keyword_image_1.jpg`) within the specified `output_dir`.

---

**File: `content/main.py`**

**Core Purpose and Logic:**
This script defines the `VideoProcessor` class, which acts as the main orchestrator for the entire YouTube video processing pipeline. It integrates and coordinates functionalities from `youtube_handler`, `transcript_processor`, `image_searcher`, and `voice_generator` to automate the process of fetching YouTube videos, processing their transcripts, finding relevant images, and generating voiceovers. It supports processing videos from a specific YouTube channel or from search results.

**Internal Dependencies:**
- `config.Config`: For loading and managing application settings.
- `youtube_handler.YouTubeHandler`: For interacting with YouTube (fetching videos, transcripts).
- `transcript_processor.TranscriptProcessor`: For AI-powered transcript rewriting and keyword extraction.
- `image_searcher.ImageSearcher`: For searching and downloading images from Pexels.
- `voice_generator.VoiceGenerator`: For generating voiceovers from text.

**External Dependencies:**
- `os`: For file system operations (though `pathlib` is preferred in this script).
- `json`: Imported but not directly used in the provided snippet.
- `pathlib.Path`: For creating and managing output directories.

**Inputs:**

**`VideoProcessor` class constructor:**
- `config_path` (str, optional): The path to the configuration JSON file. Defaults to "config.json".

**`process_channel` method:**
- `channel_url` (str): The URL of the YouTube channel to process.
- `max_videos` (int, optional): The maximum number of videos to process from the channel. Defaults to `None` (all videos).

**`process_search_results` method:**
- `search_query` (str): The search query for YouTube videos.
- `max_videos` (int, optional): The maximum number of videos to process from the search results. Defaults to 50.

**`process_video` method:**
- `video_info` (dict): A dictionary containing video details, including `id`, `title`, and `duration`.

**User Inputs (via `if __name__ == "__main__":` block):**
- Choice of processing mode (channel or search).
- YouTube channel URL or search query.
- Maximum number of videos to process.

**Files (read by the script):**
- `config.json` (indirectly, via `Config` class).

**Outputs:**

**`process_channel` method:**
- Orchestrates the processing of multiple videos from a channel.
- Prints status messages to the console.

**`process_search_results` method:**
- Orchestrates the processing of multiple videos from search results.
- Prints status messages to the console.

**`close` method:**
- Cleans up resources (e.g., closes Selenium WebDriver).

**`process_video` method:**
- Creates a unique output directory for each video.
- Saves `original_transcript.txt` and `rewritten_transcript.txt`.
- Triggers image search and download, saving images to an `images` subdirectory.
- Generates and saves `voiceover.wav`.
- Prints progress and error messages to the console.

**Files (written by the script):**
- Output directories for each video (e.g., `output/video_id_title/`).
- `original_transcript.txt`
- `rewritten_transcript.txt`
- `voiceover.wav`
- Image files within `output/video_id_title/images/`.

---

**File: `content/requirements.txt`**

**Core Purpose and Logic:**
This file lists the Python packages and their specific versions required for the project to run correctly. It serves as a manifest for dependency management, ensuring that the development and deployment environments have the necessary libraries installed.

**Internal Dependencies:**
- None

**External Dependencies:**
- None (this file *defines* external dependencies for the project).

**Inputs:**
- None (this file is read by package managers like `pip`).

**Outputs:**
- None (this file is a declaration, not an executable script).

**Key Packages Listed:**
- `google-api-python-client`: For interacting with Google APIs, specifically YouTube Data API v3.
- `youtube-transcript-api`: For fetching YouTube video transcripts.
- `openai`: For interacting with OpenAI's API (e.g., GPT models).
- `requests`: A general-purpose HTTP library for making web requests.
- `nltk`: Natural Language Toolkit, used for text processing (e.g., tokenization, stopwords).
- `edge-tts`: For generating speech using Microsoft Edge's Text-to-Speech service.
- `selenium`: For browser automation, used as a fallback for YouTube video discovery and transcript extraction when API keys are not available.
- `python-dotenv`: For loading environment variables from a `.env` file (though not explicitly used in the provided Python scripts, it's mentioned in `README.txt` for API key management).
- `pathlib`: A module for object-oriented filesystem paths (though it's a standard library module, it's listed here, possibly for clarity or specific versioning).

---

**File: `content/setup.py`**

**Core Purpose and Logic:**
This script automates the initial setup process for the project. It handles two main tasks: installing all necessary Python packages listed in `requirements.txt` (or similar dependencies) and guiding the user through the configuration of API keys and other settings, which are then saved to `config.json`. It provides a user-friendly interface for setting up the environment.

**Major Logic Blocks:**

1.  **`install_requirements` function:**
    -   Installs a predefined list of Python packages using `pip`.
    -   Ensures all project dependencies are met.

2.  **`setup_config` function:**
    -   Prompts the user for various configuration details, including API keys for YouTube, OpenAI, and Pexels, and other settings like headless browser mode, AI model, rewrite prompt, seconds per image, TTS voice, and output directory.
    -   If no YouTube API key is provided, it automatically sets `use_youtube_api` to `False`, indicating that Selenium should be used for YouTube interactions.
    -   Saves the collected configuration to `config.json`.

**Internal Dependencies:**
- None

**External Dependencies:**
- `subprocess`: For executing shell commands, specifically `pip install`.
- `sys`: For accessing `sys.executable` to ensure `pip` is run with the correct Python interpreter.
- `json`: For writing the configuration dictionary to a JSON file.

**Inputs:**

**`install_requirements` function:**
- None (reads hardcoded list of requirements).

**`setup_config` function:**
- User input via `input()` prompts for API keys and other settings.

**Outputs:**

**`install_requirements` function:**
- Installs Python packages into the current environment.
- Prints installation progress to the console.

**`setup_config` function:**
- Creates or overwrites `config.json` with the user-provided and default settings.
- Prints status messages to the console.

**Files (written by the script):**
- `config.json`

---

**File: `content/transcript_processor.py`**

**Core Purpose and Logic:**
This script defines the `TranscriptProcessor` class, which is responsible for AI-powered processing of video transcripts. It leverages OpenAI's API to rewrite transcripts for improved engagement and structure, and uses NLTK (Natural Language Toolkit) to extract keywords from the processed text, which are then used for image searching. It also handles the download of necessary NLTK data.

**Major Logic Blocks:**

1.  **NLTK Data Download (within `__init__`):**
    -   Checks if `punkt` and `stopwords` NLTK data are available. If not, it attempts to download them, ensuring the keyword extraction functionality works correctly.

2.  **`rewrite_transcript` method:**
    -   Sends the raw transcript to OpenAI's Chat Completion API.
    -   Uses a customizable system prompt (from `config`) to guide the AI in rewriting the transcript to be more engaging, clear, and well-structured.
    -   Handles potential errors during the API call and returns the original transcript as a fallback.

3.  **`extract_keywords` method:**
    -   Cleans the input text by converting to lowercase and removing non-alphanumeric characters.
    -   Tokenizes the text into individual words.
    -   Removes common English stopwords and words shorter than 4 characters to focus on more meaningful terms.
    -   Uses `collections.Counter` to find the most frequent words, returning a specified number of top keywords.

**Internal Dependencies:**
- `config.Config`: The `TranscriptProcessor` class depends on the `Config` object to retrieve OpenAI API key, AI model name, max tokens, and the rewrite prompt.

**External Dependencies:**
- `openai`: For interacting with the OpenAI API.
- `re`: For regular expression operations (text cleaning).
- `collections.Counter`: For counting word frequencies.
- `nltk`: For natural language processing tasks like tokenization and stopword removal.
    - `nltk.corpus.stopwords`: For a list of common stopwords.
    - `nltk.tokenize.word_tokenize`: For splitting text into words.

**Inputs:**

**`TranscriptProcessor` class constructor:**
- `config` (Config object): An instance of the `Config` class containing OpenAI-related settings.

**`rewrite_transcript` method:**
- `transcript` (str): The raw video transcript to be rewritten.

**`extract_keywords` method:**
- `text` (str): The text from which to extract keywords (typically the rewritten transcript).
- `num_keywords` (int, optional): The desired number of top keywords to extract. Defaults to 10.

**API Payloads (read by the script):**
- OpenAI Chat Completion API responses.

**Outputs:**

**`rewrite_transcript` method:**
- Returns the AI-rewritten transcript as a string.
- Returns the original transcript if an error occurs during AI processing.
- Prints error messages to the console.

**`extract_keywords` method:**
- Returns a list of extracted keywords (strings).
- Prints messages if NLTK data is not found.

---

**File: `content/voice_generator.py`**

**Core Purpose and Logic:**
This script defines the `VoiceGenerator` class, which is responsible for generating audio voiceovers from text using the Edge TTS (Text-to-Speech) service. It leverages `asyncio` to handle the asynchronous nature of the Edge TTS library, allowing for efficient audio generation. It also provides a method to list available voices.

**Major Logic Blocks:**

1.  **`generate_audio` method:**
    -   The main entry point for generating audio. It wraps the asynchronous `_generate_audio_async` call using `asyncio.run()`.

2.  **`_generate_audio_async` method:**
    -   An asynchronous method that uses `edge_tts.Communicate` to send text to the Edge TTS service with configured voice, rate, and volume.
    -   Saves the generated audio to the specified output path.
    -   Handles potential errors during audio generation.

3.  **`list_voices` method:**
    -   The main entry point for listing voices. It wraps the asynchronous `_list_voices_async` call using `asyncio.run()`.

4.  **`_list_voices_async` method:**
    -   An asynchronous method that uses `edge_tts.list_voices()` to fetch a list of available TTS voices.

**Internal Dependencies:**
- `config.Config`: The `VoiceGenerator` class depends on the `Config` object to retrieve TTS settings (`tts_voice`, `tts_rate`, `tts_volume`).

**External Dependencies:**
- `edge_tts`: The library for interacting with the Edge TTS service.
- `asyncio`: Python's built-in library for writing concurrent code using the async/await syntax.
- `pathlib.Path`: For handling file paths (specifically converting `output_path` to a string for `communicate.save`).

**Inputs:**

**`VoiceGenerator` class constructor:**
- `config` (Config object): An instance of the `Config` class containing TTS-related settings.

**`generate_audio` method:**
- `text` (str): The text content to convert to speech.
- `output_path` (Path or str): The file path where the generated audio (`.wav`) will be saved.

**`list_voices` method:**
- None.

**Outputs:**

**`generate_audio` method:**
- Creates an audio file (`.wav`) at the specified `output_path`.
- Prints status messages or error messages to the console.

**`list_voices` method:**
- Returns a list of available TTS voices.

---

**File: `content/youtube_handler.py`**

**Core Purpose and Logic:**
This script defines the `YouTubeHandler` class, which is responsible for all interactions with YouTube, including fetching video information (from channels or search results) and extracting video transcripts. It implements a hybrid approach, capable of using either the YouTube Data API (for speed and reliability) or Selenium (for broader access without an API key, including anti-detection features). It also includes robust error handling for transcript retrieval and duration parsing.

**Major Logic Blocks:**

1.  **Initialization (`__init__`):**
    -   Determines whether to use the YouTube API or Selenium based on the provided `config` (presence of API key and `use_youtube_api` flag).
    -   Initializes the `googleapiclient` build service for API calls or sets up the Selenium WebDriver with anti-detection options.

2.  **Selenium Setup (`setup_selenium`):**
    -   Configures `selenium.webdriver.ChromeOptions` with arguments for maximized window, anti-automation detection, and optional headless mode.
    -   Initializes `webdriver.Chrome`.

3.  **Selenium Video Discovery (`search_videos_selenium`, `get_channel_videos_selenium`):**
    -   Navigates to YouTube search results or channel video pages.
    -   Scrolls to load more videos.
    -   Extracts video IDs, titles, and URLs from the page using Selenium's `find_elements` and XPath.
    -   Includes logic to estimate video duration from visible elements.

4.  **API Video Discovery (`_search_videos_api`, `_get_channel_videos_api`):**
    -   Uses `googleapiclient.discovery.build` to interact with the YouTube Data API v3.
    -   Fetches video details (ID, snippet, contentDetails) for search queries or channel uploads.
    -   Handles pagination (`nextPageToken`) to retrieve multiple results.

5.  **Channel ID Extraction (`get_channel_id_from_url`, `_get_channel_id_from_custom_url`):**
    -   Parses various YouTube channel URL formats to extract the canonical channel ID.
    -   Includes a simplified API search fallback for custom URLs (e.g., `c/` or `@` handles).

6.  **Duration Parsing (`_parse_duration`, `_parse_duration_text`):**
    -   Converts ISO 8601 duration strings (from YouTube API) or text-based durations (from Selenium) into total seconds.

7.  **Transcript Retrieval (`get_transcript`):**
    -   Uses `youtube_transcript_api.YouTubeTranscriptApi` to fetch transcripts for a given video ID.
    -   Prioritizes English language transcripts (`en`, `en-US`, `en-GB`).
    -   Includes robust error handling for `TranscriptsDisabled` and `NoTranscriptFound` exceptions.
    -   Cleans up the retrieved transcript text by removing newlines and common tags like `[Music]`.

8.  **Resource Cleanup (`close`):**
    -   Quits the Selenium WebDriver instance if it was initialized, releasing browser resources.

**Internal Dependencies:**
- `config.Config`: The `YouTubeHandler` class depends on the `Config` object for YouTube API key, `use_youtube_api` flag, and `headless_browser` setting.

**External Dependencies:**
- `os`: For path manipulation (though not heavily used in this module).
- `re`: For regular expression operations (parsing video IDs, cleaning transcripts, parsing durations).
- `time`: For `time.sleep` (used in Selenium for waiting and rate limiting).
- `datetime`: Imported but not directly used in the provided snippet.
- `selenium`: For browser automation (WebDriver, By, Options, WebDriverWait, expected_conditions).
- `googleapiclient.discovery`: For building and interacting with YouTube Data API v3.
- `youtube_transcript_api`: For fetching YouTube video transcripts.
- `urllib.parse`: For parsing URLs (imported but not explicitly used in the provided snippet).

**Inputs:**

**`YouTubeHandler` class constructor:**
- `config` (Config object): An instance of the `Config` class containing YouTube-related settings.

**`get_channel_videos` method:**
- `channel_url` (str): The URL of the YouTube channel.
- `max_videos` (int, optional): Maximum number of videos to retrieve.

**`search_videos` method:**
- `search_query` (str): The search query.
- `max_videos` (int, optional): Maximum number of videos to retrieve.

**`get_transcript` method:**
- `video_id` (str): The ID of the YouTube video.

**API Payloads (read by the script):**
- JSON responses from YouTube Data API v3 (`search`, `videos` endpoints).

**Outputs:**

**`get_channel_videos` and `search_videos` methods:**
- Returns a list of dictionaries, each representing a video with `id`, `title`, `url`, `duration`, `published_at`, and `description`.

**`get_transcript` method:**
- Returns the cleaned transcript text as a string, or `None` if no transcript is available or an error occurs.
- Prints status and error messages to the console.

**`close` method:**
- Closes the Selenium WebDriver.
