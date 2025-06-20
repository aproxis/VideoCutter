import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QButtonGroup, QRadioButton, QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QCheckBox, QSpinBox, QTextEdit, QFileDialog, QHBoxLayout, QGroupBox, QListWidget, QListWidgetItem, QAbstractItemView, QStackedWidget, QComboBox, QSlider
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QRect, QRectF # Added QTimer, QRectF, QRect
from PyQt5.QtGui import QPixmap, QImage, QIcon, QTextOption # Added QPixmap, QImage, QIcon, QTextOption
from pathlib import Path # Added for Path object
import requests # Added for downloading images
from io import BytesIO # Added for image processing
from PIL import Image as PILImage # Added for image processing
import urllib.parse # Added for URL parsing
import re # Added for regex

# Add the directory containing this script to sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import VideoProcessor from content.main.py
from content.main import VideoProcessor
from content.utils.logger_config import setup_logging

# Set up logging for the GUI
logger = logging.getLogger(__name__)

class StreamHandler(logging.Handler):
    """Custom logging handler to emit signals for GUI updates."""
    log_signal = pyqtSignal(str) # Define a signal to emit log messages

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
        self.text_widget.setReadOnly(True) # Ensure it's read-only
        # Connect the signal to the text_widget's append method
        self.log_signal.connect(self.text_widget.append)

    def emit(self, record):
        msg = self.format(record)
        # print(f"StreamHandler received: {msg}") # Temporary print for debugging - remove after fix
        self.log_signal.emit(msg) # Emit the signal with the log message

class Worker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    log_message = pyqtSignal(str)
    results = pyqtSignal(object) # New signal to emit results

    def __init__(self, processor_func, *args, **kwargs):
        super().__init__()
        self.processor_func = processor_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.processor_func(*self.args, **self.kwargs)
            self.results.emit(result) # Emit results
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.finished.emit()

from PyQt5.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle
from PyQt5.QtGui import QFontMetrics, QStaticText # Added QStaticText


class VideoListItemDelegate(QStyledItemDelegate):
    TEXT_PADDING_TOP = 5
    TEXT_PADDING_BOTTOM = 5

    def paint(self, painter, option, index):
        video_info = index.data(Qt.UserRole)
        if not video_info:
            super().paint(painter, option, index)
            return

        # Draw the background
        super().paint(painter, option, index)

        # Get the icon and text
        icon = index.data(Qt.DecorationRole)
        text = index.data(Qt.UserRole + 1) # Get formatted text from UserRole + 1

        # Calculate positions
        rect = option.rect
        icon_size = option.widget.iconSize() # Get the icon size from the QListWidget

        # Draw icon (centered horizontally, at the top)
        icon_rect = QRect(rect.x() + (rect.width() - icon_size.width()) // 2,
                          rect.y(),
                          icon_size.width(),
                          icon_size.height())
        if icon:
            icon.paint(painter, icon_rect)

        # Draw text (below the icon, centered horizontally, with padding)
        text_rect = QRect(rect.x(),
                          rect.y() + icon_size.height() + self.TEXT_PADDING_TOP,
                          rect.width(),
                          rect.height() - icon_size.height() - self.TEXT_PADDING_TOP - self.TEXT_PADDING_BOTTOM)
        
        # Set text alignment and word wrap
        text_option = QTextOption(Qt.AlignHCenter | Qt.AlignTop)
        text_option.setWrapMode(QTextOption.WordWrap)

        # Draw the text
        painter.drawText(QRectF(text_rect), text, text_option)

    def sizeHint(self, option, index):
        video_info = index.data(Qt.UserRole)
        if not video_info:
            return super().sizeHint(option, index)

        icon_size = option.widget.iconSize()

        text = index.data(Qt.UserRole + 1) # Get formatted text from UserRole + 1
        
        # Use the grid width for text wrapping calculation
        text_width = option.widget.gridSize().width()
        
        # Calculate text height based on the actual font and wrapping
        font_metrics = QFontMetrics(option.font)
        text_rect_for_height = font_metrics.boundingRect(
            QRect(0, 0, text_width, 0), # Use 0 height to allow it to calculate required height
            Qt.AlignHCenter | Qt.AlignTop | Qt.TextWordWrap,
            text
        )
        text_height = text_rect_for_height.height()

        # Calculate total height: icon height + text height + padding
        total_height = icon_size.height() + self.TEXT_PADDING_TOP + text_height + self.TEXT_PADDING_BOTTOM

        # Ensure total_height is at least the grid height for proper selection drawing
        total_height = max(option.widget.gridSize().height(), total_height)

        # Ensure the width matches the grid size
        total_width = option.widget.gridSize().width()

        return QSize(total_width, total_height)

class ThumbnailWorker(QThread):
    thumbnail_ready = pyqtSignal(str, QIcon) # Define the signal

    def __init__(self, video_id, thumbnail_url):
        super().__init__()
        self.video_id = video_id
        self.thumbnail_url = thumbnail_url

    def run(self):
        try:
            response = requests.get(self.thumbnail_url)
            response.raise_for_status() # Raise an exception for HTTP errors
            image_data = BytesIO(response.content)
            
            # Use PIL to open and resize
            pil_image = PILImage.open(image_data)
            pil_image = pil_image.resize((180, 135), PILImage.LANCZOS) # Resize to an even larger, consistent size

            # Convert PIL Image to QPixmap
            # PIL.Image.tobytes() returns raw pixel data. QImage needs to know the format.
            # For RGB, it's usually Format_RGB888.
            qimage = QImage(pil_image.tobytes(), pil_image.width, pil_image.height, pil_image.width * 3, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            icon = QIcon(pixmap)
            
            self.thumbnail_ready.emit(self.video_id, icon)
        except Exception as e:
            logger.warning(f"Failed to load thumbnail for {self.video_id} from {self.thumbnail_url}: {e}")

class VideoCutterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Video Processor")
        self.setGeometry(100, 100, 1300, 800) # Increased initial window size
        self.setMinimumSize(1300, 800) # Set minimum size to prevent shrinking
        
        # Initialize VideoProcessor (assuming config.json is in content/)
        self.processor = VideoProcessor(config_path="content/config.json")
        
        self.all_found_videos = [] # Initialize all_found_videos
        
        # Set up logging to GUI
        self.init_ui()
        
        # Load saved GUI settings
        self.load_gui_settings()

    def setup_logging_to_gui(self):
        # Get the root logger
        root_logger = logging.getLogger()
        
        # Remove existing handlers to prevent duplicate logs
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Set the logging level to DEBUG for testing
        root_logger.setLevel(logging.DEBUG)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # File handler
        log_file_path = "app.log" # Define log file path
        log_dir = os.path.dirname(log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.DEBUG) # Set file handler to DEBUG
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Add GUI handler
        gui_handler = StreamHandler(self.log_output)
        gui_handler.setFormatter(formatter) # Use the same formatter
        gui_handler.setLevel(logging.DEBUG) # Set GUI handler to DEBUG
        root_logger.addHandler(gui_handler)
        
        logger.info("Logging set to DEBUG for GUI and file for diagnostic purposes.")
        # No need to connect gui_handler.log_signal here, it's connected in StreamHandler.__init__

    def init_ui(self):
        main_layout = QHBoxLayout() # Main layout for two columns
        main_layout.setAlignment(Qt.AlignTop) # Align content to top

        # Left Column Container Layout (Input, Search Controls, and Processing Options)
        left_column_container_layout = QVBoxLayout()
        left_column_container_layout.setAlignment(Qt.AlignTop)

        # Top-Left Block: Input Type Selection and Input Fields
        input_search_group = QGroupBox("YouTube Search & Input")
        input_search_group.setMaximumHeight(250) # Set maximum height for the group box
        input_search_layout = QHBoxLayout() # Horizontal layout for input type and search controls
        input_search_layout.setAlignment(Qt.AlignTop)

        # Left side of input_search_layout: Input Type Selection and Stacked Widget
        input_type_section_layout = QVBoxLayout()
        input_type_section_layout.setAlignment(Qt.AlignTop)

        self.input_type_group = QGroupBox("Input Type")
        input_type_layout = QVBoxLayout()
        input_type_layout.setAlignment(Qt.AlignTop)
        self.input_type_button_group = QButtonGroup(self)

        self.radio_search_query = QRadioButton("Search Query")
        self.radio_channel_url = QRadioButton("Channel URL")
        self.radio_video_url = QRadioButton("Single Video URL")

        self.input_type_button_group.addButton(self.radio_search_query, 0)
        self.input_type_button_group.addButton(self.radio_channel_url, 1)
        self.input_type_button_group.addButton(self.radio_video_url, 2)

        input_type_layout.addWidget(self.radio_search_query)
        input_type_layout.addWidget(self.radio_channel_url)
        input_type_layout.addWidget(self.radio_video_url)
        self.input_type_group.setLayout(input_type_layout)
        input_type_section_layout.addWidget(self.input_type_group)

        # Stacked Widget for Input Fields
        self.input_stacked_widget = QStackedWidget()

        # Page 0: Search Query Input
        search_query_page = QVBoxLayout()
        search_query_page.setAlignment(Qt.AlignTop)
        self.search_query_input = QLineEdit()
        self.search_query_input.setPlaceholderText("Enter search query")
        search_query_page.addWidget(self.search_query_input)

        # Duration Filter Dropdown (dynamically shown)
        self.duration_filter_combobox = QComboBox()
        self.youtube_filter_param = "" # Stores the selected filter param

        filters = {
            "No filter": "",
            "Latest (this month)": "&sp=CAISBAgEEAE",
            "Latest (this month, 4-20 min)": "&sp=CAISBggEEAEYAw",
            "Latest (this month, >20 min)": "&sp=CAISBggEEAEYAg",
            "Most viewed (this month)": "&sp=CAMSBggEEAEYAg",
            "Most viewed (this month, 4-20 min)": "&sp=CAMSBggEEAEYAw",
            "Most viewed (this month, >20 min)": "&sp=CAMSBggEEAEYAg"
        }

        for text, param in filters.items():
            self.duration_filter_combobox.addItem(text, param)
        
        self.duration_filter_combobox.currentIndexChanged.connect(self.on_duration_filter_changed) # Connect the signal
        search_query_page.addWidget(self.duration_filter_combobox)
        
        search_query_widget = QWidget()
        search_query_widget.setLayout(search_query_page)
        self.input_stacked_widget.addWidget(search_query_widget)

        # Page 1: Channel URL Input
        channel_url_page = QVBoxLayout()
        channel_url_page.setAlignment(Qt.AlignTop)
        self.channel_url_input = QLineEdit()
        self.channel_url_input.setPlaceholderText("Enter channel URL")
        channel_url_page.addWidget(self.channel_url_input)
        channel_url_widget = QWidget()
        channel_url_widget.setLayout(channel_url_page)
        self.input_stacked_widget.addWidget(channel_url_widget)

        # Page 2: Single Video URL Input
        video_url_page = QVBoxLayout()
        video_url_page.setAlignment(Qt.AlignTop)
        self.video_url_input = QLineEdit()
        self.video_url_input.setPlaceholderText("Enter single video URL")
        video_url_page.addWidget(self.video_url_input)
        
        # Add the "Search by Video ID" button directly to the video_url_page layout
        self.search_by_video_id_button = QPushButton("Search by Video ID")
        video_url_page.addWidget(self.search_by_video_id_button)

        video_url_widget = QWidget()
        video_url_widget.setLayout(video_url_page)
        self.input_stacked_widget.addWidget(video_url_widget)

        input_type_section_layout.addWidget(self.input_stacked_widget)
        input_search_layout.addLayout(input_type_section_layout) # Add input type and stacked widget to left of input_search_layout

        # Right side of input_search_layout: Max Videos and Search Button
        search_controls_layout = QVBoxLayout()
        search_controls_layout.setAlignment(Qt.AlignTop)

        self.max_videos_label = QLabel("Max Videos to Process:")
        self.max_videos_spinbox = QSpinBox()
        self.max_videos_spinbox.setRange(1, 1000)
        self.max_videos_spinbox.setValue(50)
        search_controls_layout.addWidget(self.max_videos_label)
        search_controls_layout.addWidget(self.max_videos_spinbox)

        self.search_button = QPushButton("Search YouTube")
        search_controls_layout.addWidget(self.search_button)

        input_search_layout.addLayout(search_controls_layout) # Add search controls to right of input_search_layout
        input_search_group.setLayout(input_search_layout)
        left_column_container_layout.addWidget(input_search_group) # Add top-left block to left column

        # Processing Options Group (moved to left column, below input_search_group)
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()
        options_layout.setAlignment(Qt.AlignTop)

        self.rewrite_checkbox = QCheckBox("Rewrite Transcript")
        self.rewrite_checkbox.setChecked(True)
        options_layout.addWidget(self.rewrite_checkbox)

        # Conditional Rewrite Prompt Field
        self.rewrite_prompt_textedit = QTextEdit()
        self.rewrite_prompt_textedit.setPlaceholderText("Enter custom rewrite prompt...")
        self.rewrite_prompt_textedit.setMinimumHeight(60)
        self.rewrite_prompt_textedit.setMaximumHeight(120)
        # Load default prompt from config
        self.rewrite_prompt_textedit.setText(self.processor.config.rewrite_prompt)
        options_layout.addWidget(self.rewrite_prompt_textedit)
        # Connect checkbox to toggle visibility and enabled state
        self.rewrite_checkbox.toggled.connect(self.update_rewrite_prompt_field_state)
        self.update_rewrite_prompt_field_state(self.rewrite_checkbox.isChecked()) # Set initial state

        self.voiceover_checkbox = QCheckBox("Generate Voiceover")
        self.voiceover_checkbox.setChecked(True)
        options_layout.addWidget(self.voiceover_checkbox)

        self.download_images_checkbox = QCheckBox("Download Images")
        self.download_images_checkbox.setChecked(True)
        options_layout.addWidget(self.download_images_checkbox)

        self.seconds_per_image_label = QLabel("Seconds per Image:")
        self.seconds_per_image_spinbox = QSpinBox()
        self.seconds_per_image_spinbox.setRange(1, 60)
        self.seconds_per_image_spinbox.setValue(5) # Default value
        options_layout.addWidget(self.seconds_per_image_label)
        options_layout.addWidget(self.seconds_per_image_spinbox)

        self.download_pexels_videos_checkbox = QCheckBox("Download Pexels Videos")
        self.download_pexels_videos_checkbox.setChecked(False) # Default to false
        options_layout.addWidget(self.download_pexels_videos_checkbox)

        self.num_pexels_videos_label = QLabel("Number of Pexels Videos:")
        self.num_pexels_videos_spinbox = QSpinBox()
        self.num_pexels_videos_spinbox.setRange(0, 100)
        self.num_pexels_videos_spinbox.setValue(0) # Default to 0
        options_layout.addWidget(self.num_pexels_videos_label)
        options_layout.addWidget(self.num_pexels_videos_spinbox)

        options_group.setLayout(options_layout)
        left_column_container_layout.addWidget(options_group) # Add processing options to left column

        # Action Buttons (remain at bottom of left column)
        action_layout = QHBoxLayout()
        action_layout.setAlignment(Qt.AlignTop)
        self.run_selected_button = QPushButton("Process Selected Video")
        self.run_selected_button.setEnabled(False) # Disabled until a video is selected
        action_layout.addWidget(self.run_selected_button)

        self.run_all_button = QPushButton("Process All Videos")
        action_layout.addWidget(self.run_all_button)
        left_column_container_layout.addLayout(action_layout)

        main_layout.addLayout(left_column_container_layout) # Add left column container to main layout

        # Right Column Layout (Results and Duration Filters)
        right_column_layout = QVBoxLayout()
        right_column_layout.setAlignment(Qt.AlignTop)

        # Duration Range Sliders (moved to right column)
        duration_range_group = QGroupBox("Duration Range (minutes)")
        duration_range_layout = QVBoxLayout()
        duration_range_layout.setAlignment(Qt.AlignTop)

        # Min Duration Input (SpinBox and Slider)
        min_duration_layout = QHBoxLayout()
        self.min_duration_spinbox_input = QSpinBox()
        self.min_duration_spinbox_input.setRange(0, 600) # 0 to 10 hours in minutes
        self.min_duration_spinbox_input.setValue(0)
        self.min_duration_slider = QSlider(Qt.Horizontal)
        self.min_duration_slider.setRange(0, 600) # 0 to 10 hours in minutes
        self.min_duration_slider.setValue(0)
        self.min_duration_slider.setTickPosition(QSlider.TicksBelow)
        self.min_duration_slider.setTickInterval(60) # Every hour
        min_duration_layout.addWidget(QLabel("Min (min):"))
        min_duration_layout.addWidget(self.min_duration_spinbox_input)
        min_duration_layout.addWidget(self.min_duration_slider)
        duration_range_layout.addLayout(min_duration_layout)

        # Max Duration Input (SpinBox and Slider)
        max_duration_layout = QHBoxLayout()
        self.max_duration_spinbox_input = QSpinBox()
        self.max_duration_spinbox_input.setRange(0, 600) # 0 to 10 hours in minutes
        self.max_duration_spinbox_input.setValue(600)
        self.max_duration_slider = QSlider(Qt.Horizontal)
        self.max_duration_slider.setRange(0, 600) # 0 to 10 hours in minutes
        self.max_duration_slider.setValue(600)
        self.max_duration_slider.setTickPosition(QSlider.TicksBelow)
        self.max_duration_slider.setTickInterval(60) # Every hour
        max_duration_layout.addWidget(QLabel("Max (min):"))
        max_duration_layout.addWidget(self.max_duration_spinbox_input)
        max_duration_layout.addWidget(self.max_duration_slider)
        duration_range_layout.addLayout(max_duration_layout)

        duration_range_group.setLayout(duration_range_layout)
        right_column_layout.addWidget(duration_range_group)

        # Video List Display
        self.video_list_label = QLabel("Found Videos:")
        right_column_layout.addWidget(self.video_list_label)
        self.video_list_widget = QListWidget()
        self.video_list_widget.setSelectionMode(QAbstractItemView.ExtendedSelection) # Allow multiple selection
        self.video_list_widget.setIconSize(QSize(180, 135)) # Set icon size to match thumbnail
        self.video_list_widget.setUniformItemSizes(True) # Optimize rendering for uniform sizes
        self.video_list_widget.setViewMode(QListWidget.IconMode) # Display items in a grid
        self.video_list_widget.setGridSize(QSize(200, 220)) # Set grid cell size (width, height) - Increased height for text
        # self.video_list_widget.setResizeMode(QListWidget.Adjust) # Removed: can cause shrinking issues
        self.video_list_widget.setWordWrap(True) # Allow text to wrap
        self.video_list_widget.setMinimumHeight(400) # Ensure minimum height for the list widget
        self.video_list_widget.setItemDelegate(VideoListItemDelegate()) # Set custom delegate
        self.video_list_widget.setDragEnabled(False) # Disable dragging of items
        right_column_layout.addWidget(self.video_list_widget) # Add video list to right column

        # Log Output (moved to bottom of right column)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        right_column_layout.addWidget(self.log_output)

        main_layout.addLayout(right_column_layout) # Add right column to main layout

        self.setLayout(main_layout)

        # Connect signals to slots
        self.search_button.clicked.connect(self.perform_youtube_search)
        self.search_by_video_id_button.clicked.connect(self.initiate_search_by_video_id) # Connect new button
        self.run_all_button.clicked.connect(self.start_processing_all_videos)
        self.run_selected_button.clicked.connect(self.start_processing_selected_videos)
        self.video_list_widget.itemSelectionChanged.connect(self.update_run_selected_button_state)
        
        # Connect input type radio buttons
        self.input_type_button_group.buttonClicked[int].connect(self.input_stacked_widget.setCurrentIndex)
        self.radio_search_query.setChecked(True) # Set default selection

        # Connect duration sliders
        self.min_duration_slider.valueChanged.connect(self.on_min_duration_changed)
        self.max_duration_slider.valueChanged.connect(self.on_max_duration_changed)
        self.min_duration_spinbox_input.valueChanged.connect(self.on_min_duration_changed)
        self.max_duration_spinbox_input.valueChanged.connect(self.on_max_duration_changed)
        
    def on_duration_filter_changed(self, index):
        """Handles changes in the duration filter combobox."""
        self.youtube_filter_param = self.duration_filter_combobox.itemData(index)
        logger.info(f"YouTube filter changed to: {self.youtube_filter_param}")

    def load_gui_settings(self):
        """Loads GUI settings from config and applies them."""
        settings = self.processor.config.load_gui_settings()
        
        # Input Type
        input_type_id = settings.get('input_type_id', 0)
        # Ensure the button exists before setting checked
        button = self.input_type_button_group.button(input_type_id)
        if button:
            button.setChecked(True)
        self.input_stacked_widget.setCurrentIndex(input_type_id)

        # Input Fields
        self.search_query_input.setText(settings.get('search_query', ''))
        self.channel_url_input.setText(settings.get('channel_url', ''))
        self.video_url_input.setText(settings.get('video_url', ''))
        self.max_videos_spinbox.setValue(settings.get('max_videos', 50))

        # Duration Filter Dropdown
        duration_filter_param = settings.get('youtube_filter_param', '')
        index = self.duration_filter_combobox.findData(duration_filter_param)
        if index != -1:
            self.duration_filter_combobox.setCurrentIndex(index)
        
        # Duration Sliders and SpinBoxes
        self.min_duration_slider.setValue(settings.get('min_duration_slider', 0))
        self.min_duration_spinbox_input.setValue(settings.get('min_duration_slider', 0))
        self.max_duration_slider.setValue(settings.get('max_duration_slider', 600))
        self.max_duration_spinbox_input.setValue(settings.get('max_duration_slider', 600))
        self.apply_duration_filter() # Apply filter immediately after loading settings
        # No need to call on_duration_slider_changed here, as apply_duration_filter is called directly

        # Processing Options
        self.rewrite_checkbox.setChecked(settings.get('rewrite_transcript', True))
        self.rewrite_prompt_textedit.setText(settings.get('rewrite_prompt_text', self.processor.config.rewrite_prompt))
        self.voiceover_checkbox.setChecked(settings.get('generate_voiceover', True))
        self.download_images_checkbox.setChecked(settings.get('download_images', True))
        self.seconds_per_image_spinbox.setValue(settings.get('seconds_per_image', 5))
        self.download_pexels_videos_checkbox.setChecked(settings.get('download_pexels_videos', False))
        self.num_pexels_videos_spinbox.setValue(settings.get('num_pexels_videos', 0))

        logger.info("GUI settings loaded.")

    def closeEvent(self, event):
        """Overrides the close event to save GUI settings."""
        self.save_gui_settings()
        super().closeEvent(event)

    def save_gui_settings(self):
        """Gathers current GUI settings and saves them to config."""
        settings = {
            'input_type_id': self.input_type_button_group.checkedId(),
            'search_query': self.search_query_input.text(),
            'channel_url': self.channel_url_input.text(),
            'video_url': self.video_url_input.text(),
            'max_videos': self.max_videos_spinbox.value(),
            'youtube_filter_param': self.youtube_filter_param,
            'min_duration_slider': self.min_duration_slider.value(), # Save slider value
            'max_duration_slider': self.max_duration_slider.value(), # Save slider value
            'min_duration_spinbox': self.min_duration_spinbox_input.value(), # Save spinbox value
            'max_duration_spinbox': self.max_duration_spinbox_input.value(), # Save spinbox value
            'rewrite_transcript': self.rewrite_checkbox.isChecked(),
            'rewrite_prompt_text': self.rewrite_prompt_textedit.toPlainText(),
            'generate_voiceover': self.voiceover_checkbox.isChecked(),
            'download_images': self.download_images_checkbox.isChecked(),
            'seconds_per_image': self.seconds_per_image_spinbox.value(),
            'download_pexels_videos': self.download_pexels_videos_checkbox.isChecked(),
            'num_pexels_videos': self.num_pexels_videos_spinbox.value(),
        }
        self.processor.config.save_gui_settings(settings)
        logger.info("GUI settings saved.")

    def on_min_duration_changed(self, value):
        """Handles changes in min duration slider or spinbox."""
        # Update the other control if changed from one
        if self.sender() == self.min_duration_slider:
            self.min_duration_spinbox_input.setValue(value)
        else: # sender is min_duration_spinbox_input
            self.min_duration_slider.setValue(value)
        
        # Ensure min <= max
        if self.min_duration_slider.value() > self.max_duration_slider.value():
            self.max_duration_slider.setValue(self.min_duration_slider.value())
            self.max_duration_spinbox_input.setValue(self.min_duration_slider.value())
        
        self.apply_duration_filter() # Apply filter immediately

    def on_max_duration_changed(self, value):
        """Handles changes in max duration slider or spinbox."""
        # Update the other control if changed from one
        if self.sender() == self.max_duration_slider:
            self.max_duration_spinbox_input.setValue(value)
        else: # sender is max_duration_spinbox_input
            self.max_duration_slider.setValue(value)

        # Ensure max >= min
        if self.max_duration_slider.value() < self.min_duration_slider.value():
            self.min_duration_slider.setValue(self.max_duration_slider.value())
            self.min_duration_spinbox_input.setValue(self.max_duration_slider.value())
        
        self.apply_duration_filter() # Apply filter immediately

    def set_ui_enabled(self, enabled):
        logger.debug(f"set_ui_enabled called with enabled={enabled}") # Add this line
        # Enable/disable input fields based on current stacked widget index
        current_index = self.input_stacked_widget.currentIndex()
        
        # Explicitly enable/disable the input type group and radio buttons
        self.input_type_group.setEnabled(enabled) # Enable/disable the group box
        self.radio_search_query.setEnabled(enabled)
        self.radio_channel_url.setEnabled(enabled)
        self.radio_video_url.setEnabled(enabled)

        self.search_query_input.setEnabled(enabled)
        self.duration_filter_combobox.setEnabled(enabled)
        self.channel_url_input.setEnabled(enabled)
        self.video_url_input.setEnabled(enabled)

        self.max_videos_spinbox.setEnabled(enabled)
        self.min_duration_slider.setEnabled(enabled) # Changed from spinbox
        self.max_duration_slider.setEnabled(enabled) # Changed from spinbox
        self.rewrite_checkbox.setEnabled(enabled)
        
        # The enabled state of rewrite_prompt_textedit is now managed by update_rewrite_prompt_field_state
        # based on the rewrite_checkbox's state.
        
        self.voiceover_checkbox.setEnabled(enabled)
        self.download_images_checkbox.setEnabled(enabled)
        self.seconds_per_image_spinbox.setEnabled(enabled)
        self.download_pexels_videos_checkbox.setEnabled(enabled)
        self.num_pexels_videos_spinbox.setEnabled(enabled)
        self.search_button.setEnabled(enabled)
        self.run_all_button.setEnabled(enabled and self.video_list_widget.count() > 0)
        self.update_run_selected_button_state() # Update based on selection

    def update_run_selected_button_state(self):
        self.run_selected_button.setEnabled(len(self.video_list_widget.selectedItems()) > 0)

    def perform_youtube_search(self):
        search_query = self.search_query_input.text().strip()
        channel_url = self.channel_url_input.text().strip()
        video_url = self.video_url_input.text().strip() # Get single video URL
        max_videos = self.max_videos_spinbox.value()
        
        self.set_ui_enabled(False)
        self.log_output.clear()
        self.video_list_widget.clear()
        logger.info("Starting YouTube search...")

        current_input_type = self.input_type_button_group.checkedId()

        if current_input_type == 0: # YouTube Search Query
            if not search_query:
                logger.warning("Please enter a search query.")
                self.set_ui_enabled(True)
                return
            self.worker = Worker(
                self.processor.process_search_results,
                search_query,
                max_videos=max_videos,
                # min_length and max_length are no longer passed here
                generate_voiceover=False,
                rewrite_transcript=False,
                download_images=False,
                seconds_per_image=self.processor.config.seconds_per_image,
                download_pexels_videos=False,
                num_pexels_videos=0,
                youtube_filter=self.youtube_filter_param
            )
        elif current_input_type == 1: # YouTube Channel URL
            if not channel_url:
                logger.warning("Please enter a channel URL.")
                self.set_ui_enabled(True)
                return
            self.worker = Worker(
                self.processor.process_channel,
                channel_url,
                max_videos=max_videos,
                # min_length and max_length are no longer passed here
                generate_voiceover=False,
                rewrite_transcript=False,
                download_images=False,
                seconds_per_image=self.processor.config.seconds_per_image,
                download_pexels_videos=False,
                num_pexels_videos=0,
                youtube_filter="" # Filters are only for search, not channels
            )
        elif current_input_type == 2: # Direct One Video URL
            if not video_url:
                logger.warning("Please enter a single video URL.")
                self.set_ui_enabled(True)
                return
            self.worker = Worker(
                self.processor.process_single_video,
                video_url,
                generate_voiceover=False,
                rewrite_transcript=False,
                download_images=False,
                seconds_per_image=self.processor.config.seconds_per_image,
                download_pexels_videos=False,
                num_pexels_videos=0
            )
        else:
            logger.warning("No input type selected.")
            self.set_ui_enabled(True)
            return
        
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.results.connect(self.on_search_results) # Connect results signal
        self.worker.start()

    def on_search_finished(self):
        logger.info("YouTube search completed.")
        self.set_ui_enabled(True)

    def on_search_results(self, results_tuple):
        self.video_list_widget.clear()
        self.all_found_videos = results_tuple[0] # Store all found videos
        self.current_run_output_dir = results_tuple[2] # Extract run_output_dir
        
        # No need for this check here, apply_duration_filter will handle empty list
        # if not self.all_found_videos:
        #     logger.info("No videos found matching your criteria.")
        #     return

        self.apply_duration_filter() # Apply filter after search completes
        logger.info(f"Found {len(self.all_found_videos)} videos. Displaying {self.video_list_widget.count()} after filter.")
        self.update_run_selected_button_state() # Update button state after populating list
        
        # Force a redraw and layout update, deferred to allow GUI to settle
        QTimer.singleShot(100, self.video_list_widget.update)
        QTimer.singleShot(100, self.video_list_widget.repaint)
        # Explicitly update geometries to force layout recalculation
        QTimer.singleShot(100, self.video_list_widget.updateGeometries)
        QTimer.singleShot(100, self.video_list_widget.viewport().update) # Force viewport redraw
        # Removed adjustSize calls as they can cause shrinking issues
        # QTimer.singleShot(100, self.video_list_widget.adjustSize)
        # QTimer.singleShot(100, self.video_list_widget.parentWidget().adjustSize)

    def apply_duration_filter(self):
        """Applies the duration filter to the all_found_videos and updates the QListWidget."""
        self.video_list_widget.clear()
        min_duration_seconds = self.min_duration_slider.value() * 60
        max_duration_seconds = self.max_duration_slider.value() * 60

        filtered_videos = []
        for video_info in self.all_found_videos:
            if min_duration_seconds <= video_info['duration'] <= max_duration_seconds:
                filtered_videos.append(video_info)
        
        for i, video_info in enumerate(filtered_videos): # Added enumerate for numbering
            logger.debug(f"on_search_results: video_info['duration'] type: {type(video_info['duration'])}, value: {video_info['duration']}")
            
            # Format duration for display
            duration_seconds = video_info['duration']
            hours = duration_seconds // 3600
            minutes = (duration_seconds % 3600) // 60
            seconds = duration_seconds % 60
            
            if hours > 0:
                duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes:02d}:{seconds:02d}"

            # New format: thumb number. (duration) title
            item_text = f"{i+1}. ({duration_str}) {video_info['title']}"
            item = QListWidgetItem("") # Set empty text to prevent default drawing
            item.setData(Qt.UserRole, video_info) # Store the full video_info dictionary
            item.setData(Qt.UserRole + 1, item_text) # Store the formatted text for the delegate
            self.video_list_widget.addItem(item)

            # Start thumbnail download in a separate thread
            thumbnail_url = video_info.get('thumbnail_url')
            if thumbnail_url:
                thumbnail_worker = ThumbnailWorker(video_info['id'], thumbnail_url)
                thumbnail_worker.thumbnail_ready.connect(self.on_thumbnail_ready)
                thumbnail_worker.start() # Start the worker thread
                # Store a reference to the worker to prevent it from being garbage collected
                # before it finishes. A simple list is sufficient.
                if not hasattr(self, '_thumbnail_workers'):
                    self._thumbnail_workers = []
                self._thumbnail_workers.append(thumbnail_worker)

    def on_thumbnail_ready(self, video_id, icon):
        """Slot to update the QListWidgetItem with the downloaded thumbnail."""
        for i in range(self.video_list_widget.count()):
            item = self.video_list_widget.item(i)
            video_info = item.data(Qt.UserRole)
            if video_info and video_info.get('id') == video_id:
                item.setIcon(icon)
                break

    def on_search_error(self, error_message):
        logger.error(f"YouTube search failed: {error_message}")
        self.set_ui_enabled(True)

    def on_search_error(self, error_message):
        logger.error(f"YouTube search failed: {error_message}")
        self.set_ui_enabled(True)

    def start_processing_all_videos(self):
        if self.video_list_widget.count() == 0:
            logger.warning("No videos found to process. Please perform a search first.")
            return
        
        videos_to_process = []
        for i in range(self.video_list_widget.count()):
            item = self.video_list_widget.item(i)
            videos_to_process.append(item.data(Qt.UserRole)) # Retrieve stored video_info

        self._start_video_processing_worker(videos_to_process)

    def start_processing_selected_videos(self):
        selected_items = self.video_list_widget.selectedItems()
        if not selected_items:
            logger.warning("No videos selected to process.")
            return
        
        videos_to_process = [item.data(Qt.UserRole) for item in selected_items]
        self._start_video_processing_worker(videos_to_process)

    def _start_video_processing_worker(self, videos_to_process):
        # Get rewrite prompt from GUI
        rewrite_prompt = self.rewrite_prompt_textedit.toPlainText() if self.rewrite_checkbox.isChecked() else self.processor.config.rewrite_prompt
        
        rewrite_transcript = self.rewrite_checkbox.isChecked()
        generate_voiceover = self.voiceover_checkbox.isChecked()
        download_images = self.download_images_checkbox.isChecked()
        seconds_per_image = self.seconds_per_image_spinbox.value()
        download_pexels_videos = self.download_pexels_videos_checkbox.isChecked()
        num_pexels_videos = self.num_pexels_videos_spinbox.value()

        self.set_ui_enabled(False)
        self.log_output.clear()
        logger.info(f"Starting processing for {len(videos_to_process)} video(s)...")
        logger.info(f"Processing options: Rewrite={rewrite_transcript}, Voiceover={generate_voiceover}, Download Images={download_images}, Seconds/Image={seconds_per_image}, Download Pexels Videos={download_pexels_videos}, Num Pexels Videos={num_pexels_videos}")

        self.processing_worker = ProcessVideosWorker(
            self.processor,
            videos_to_process,
            generate_voiceover,
            rewrite_transcript,
            download_images,
            seconds_per_image,
            download_pexels_videos,
            num_pexels_videos,
            self.current_run_output_dir, # Pass the run_output_dir
            rewrite_prompt=rewrite_prompt # Pass the custom rewrite prompt
        )
        self.processing_worker.finished.connect(self.on_processing_finished)
        self.processing_worker.error.connect(self.on_processing_error)
        self.processing_worker.start()

    def on_processing_finished(self):
        logger.info("Video processing completed.")
        self.set_ui_enabled(True)

    def on_processing_error(self, error_message):
        logger.error(f"Video processing failed: {error_message}")
        self.set_ui_enabled(True)

    def update_rewrite_prompt_field_state(self, checked):
        """Updates the visibility and enabled state of the rewrite prompt text field."""
        self.rewrite_prompt_textedit.setVisible(checked)
        self.rewrite_prompt_textedit.setEnabled(checked)

    def initiate_search_by_video_id(self):
        video_url = self.video_url_input.text().strip()
        if not video_url:
            logger.warning("Please enter a video URL to search by ID.")
            return

        self.set_ui_enabled(False)
        self.log_output.clear()
        logger.info(f"Attempting to extract video ID from URL: {video_url} for search...")

        self.video_id_extraction_worker = Worker(self._extract_video_id_for_search, video_url)
        self.video_id_extraction_worker.results.connect(self.on_video_id_extracted_for_search)
        self.video_id_extraction_worker.finished.connect(lambda: self.set_ui_enabled(True)) # Re-enable UI on finish
        self.video_id_extraction_worker.error.connect(self.on_video_id_extraction_error)
        self.video_id_extraction_worker.start()

    def _extract_video_id_for_search(self, video_url):
        """Helper function to extract video ID directly from URL without Selenium navigation."""
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
                    logger.warning(f"Could not extract video ID from search results URL: {video_url}")
            else:
                # Standard video ID extraction from watch?v= or youtu.be/
                video_id_match = re.search(r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:&|\?|$)', video_url)
                if video_id_match:
                    video_id = video_id_match.group(1)
                    logger.info(f"Extracted video ID '{video_id}' from standard video URL.")
                else:
                    logger.warning(f"Could not extract video ID from URL: {video_url}")
        except Exception as e:
            logger.error(f"Error parsing video ID from URL {video_url}: {str(e)}", exc_info=True)
        return video_id

    def on_video_id_extracted_for_search(self, video_id):
        if video_id:
            logger.info(f"Video ID '{video_id}' extracted. Initiating search...")
            self.radio_search_query.setChecked(True) # Switch to Search Query mode
            self.input_stacked_widget.setCurrentIndex(0) # Explicitly set stacked widget to Search Query page
            self.search_query_input.setText(video_id) # Populate search query with video ID
            self.perform_youtube_search() # Trigger the search
        else:
            logger.warning("Failed to extract video ID from the provided URL.")
            self.set_ui_enabled(True) # Ensure UI is re-enabled if extraction fails

    def on_video_id_extraction_error(self, error_message):
        logger.error(f"Error during video ID extraction: {error_message}")
        self.set_ui_enabled(True) # Ensure UI is re-enabled on error

class ProcessVideosWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, processor, videos, generate_voiceover, rewrite_transcript, download_images, seconds_per_image, download_pexels_videos, num_pexels_videos, run_output_dir, rewrite_prompt):
        super().__init__()
        self.processor = processor
        self.videos = videos
        self.generate_voiceover = generate_voiceover
        self.rewrite_transcript = rewrite_transcript
        self.download_images = download_images
        self.seconds_per_image = seconds_per_image
        self.download_pexels_videos = download_pexels_videos
        self.num_pexels_videos = num_pexels_videos
        self.run_output_dir = run_output_dir # Store the run_output_dir
        self.rewrite_prompt = rewrite_prompt # Store the rewrite prompt

    def run(self):
        try:
            self.processor._process_videos_list(
                self.videos, # This is videos_to_process
                self.run_output_dir,
                generate_voiceover=self.generate_voiceover,
                rewrite_transcript=self.rewrite_transcript,
                download_images=self.download_images,
                seconds_per_image=self.seconds_per_image,
                download_pexels_videos=self.download_pexels_videos,
                num_pexels_videos=self.num_pexels_videos,
                rewrite_prompt=self.rewrite_prompt # Pass the rewrite prompt
            )
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = VideoCutterGUI()
    gui.show()
    sys.exit(app.exec_())
