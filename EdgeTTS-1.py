import sys
import asyncio
import os
import edge_tts
import collections
import traceback # For detailed error logging
import time
import logging

# --- ИЗМЕНЕНИЕ: Импорт winsound для Windows ---
if sys.platform == "win32":
    try:
        import winsound
    except ImportError:
        print("WARNING: Модуль winsound не найден, звуковые уведомления будут недоступны.")
        winsound = None # Определяем как None, чтобы проверки ниже работали
else:
    winsound = None # Не Windows, звуков не будет
# --- КОНЕЦ ИЗМЕНЕНИЯ ---

try:
    import docx
    DOCX_SUPPORTED = True
except ImportError:
    DOCX_SUPPORTED = False

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QFileDialog, QComboBox, QSlider, QMessageBox,
    QTextEdit, QSizePolicy, QSpacerItem, QProgressBar
)
from PyQt5.QtCore import (
    Qt, QThread, pyqtSignal, QEvent, QCoreApplication, QTimer
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem

# --- Helper function to log errors ---
def log_error(message):
    """Записывает сообщение об ошибке в файл error.txt и выводит в консоль."""
    try:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace_info = ""
        if exc_type is not None:
            trace_info = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            message += f"\nTraceback:\n{trace_info}"

        log_file = "edge_tts_error.log"
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            f.write(f"{timestamp} - {message}\n")
    except Exception as e:
        print(f"Критическая ошибка записи в лог ({log_file}): {e}")
        print(f"Исходное сообщение: {message}")
        if trace_info: print(f"Traceback:\n{trace_info}")

# --- Globals ---
VOICE_MAP = {} # Populated by VoiceLoaderThread

# --- Worker Threads ---

class VoiceLoaderThread(QThread):
    """Loads voices in a separate thread using asyncio."""
    voices_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    async def _fetch_voices_async(self):
        self.log_message.emit("Запрос списка голосов от Edge TTS...")
        return await edge_tts.list_voices()

    def run(self):
        """Executes the voice fetching process using asyncio.run()."""
        global VOICE_MAP
        try:
            voices = asyncio.run(self._fetch_voices_async())

            if not voices:
                raise Exception("Получен пустой список голосов.")

            VOICE_MAP = {v.get('ShortName', ''): v.get('Name', '') for v in voices if v.get('ShortName') and v.get('Name')}
            if not VOICE_MAP:
                 try: self.log_message.emit("Предупреждение: Не удалось создать карту голосов (VOICE_MAP).")
                 except RuntimeError: print("VoiceLoaderThread: Предупреждение: Не удалось создать карту голосов (VOICE_MAP).")

            try:
                self.log_message.emit(f"Найдено {len(voices)} голосов.")
                self.voices_loaded.emit(voices)
            except RuntimeError:
                 print(f"VoiceLoaderThread: Найдено {len(voices)} голосов. (сигнал не отправлен)")

        except Exception as e:
            error_msg = f"Не удалось загрузить голоса: {e}"
            log_error(f"Ошибка в VoiceLoaderThread: {error_msg}")
            try: self.error_occurred.emit(error_msg)
            except RuntimeError: print(f"VoiceLoaderThread: Ошибка загрузки голосов: {error_msg} (сигнал не отправлен)")


class TTSWorker(QThread):
    """Handles the text-to-speech synthesis in a separate thread."""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    log_message = pyqtSignal(str)
    progress_update = pyqtSignal(int)

    def __init__(self, text, voice, output_file, rate_str, volume_str, pitch_str, parent=None):
        super().__init__(parent)
        self.text = text
        self.voice = voice
        self.output_file = output_file
        self.rate_str = rate_str
        self.volume_str = volume_str
        self.pitch_str = pitch_str
        self._is_running = True
        self._current_task = None

    async def _run_tts(self):
        self._current_task = asyncio.current_task()
        try:
            if not self._is_running:
                 self.log_message.emit("Синтез отменен перед запуском Communicate.")
                 return

            self.log_message.emit(f"Начало синтеза: Голос='{self.voice}', Rate='{self.rate_str}', Vol='{self.volume_str}', Pitch='{self.pitch_str}'")
            self.progress_update.emit(10)

            communicate = edge_tts.Communicate(
                self.text, self.voice, rate=self.rate_str,
                volume=self.volume_str
            )
            await asyncio.sleep(0)
            self.progress_update.emit(30)

            if not self._is_running:
                 self.log_message.emit("Синтез отменен перед сохранением файла.")
                 return

            self.log_message.emit(f"Сохранение аудио в: {os.path.basename(self.output_file)}...")
            output_dir = os.path.dirname(self.output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                self.log_message.emit(f"Создана директория: {output_dir}")

            save_coro = communicate.save(self.output_file)
            save_task = asyncio.create_task(save_coro)

            progress_value = 30
            while not save_task.done():
                if not self._is_running:
                    self.log_message.emit("Остановка во время сохранения файла...")
                    save_task.cancel()
                    try: await save_task
                    except asyncio.CancelledError:
                         self.log_message.emit("Задача сохранения файла успешно отменена.")
                         if os.path.exists(self.output_file):
                             try:
                                 os.remove(self.output_file)
                                 self.log_message.emit(f"Удален частично сохраненный файл: {self.output_file}")
                             except OSError as e_rem:
                                 self.log_message.emit(f"Не удалось удалить частичный файл {self.output_file}: {e_rem}")
                         self.error.emit("Синтез прерван пользователем во время сохранения.")
                         self.progress_update.emit(0)
                         return
                    except Exception as e_wait:
                        log_error(f"Неожиданная ошибка при ожидании отмены задачи сохранения: {e_wait}")
                        self.error.emit(f"Ошибка при отмене сохранения: {e_wait}")
                        self.progress_update.emit(0)
                        return

                progress_value = min(95, progress_value + 2)
                self.progress_update.emit(progress_value)
                try:
                    await asyncio.wait_for(asyncio.shield(save_task), timeout=0.2)
                except asyncio.TimeoutError: pass
                except asyncio.CancelledError:
                     self.log_message.emit("Задача _run_tts отменена во время ожидания сохранения.")
                     if not save_task.done(): save_task.cancel()
                     raise
                except Exception as e_wait_inner:
                     log_error(f"Ошибка задачи сохранения внутри цикла ожидания: {e_wait_inner}")
                     self.error.emit(f"Ошибка сохранения: {e_wait_inner}")
                     self.progress_update.emit(0)
                     return

            if save_task.done() and not save_task.cancelled():
                exc = save_task.exception()
                if exc:
                    log_error(f"Задача сохранения завершилась с ошибкой: {exc}")
                    self.error.emit(f"Ошибка сохранения файла: {exc}")
                    self.progress_update.emit(0)
                elif self._is_running:
                    self.progress_update.emit(100)
                    self.log_message.emit("Синтез и сохранение успешно завершены.")
                    self.finished.emit(self.output_file)
                else:
                    self.log_message.emit("Сохранение завершилось, но флаг остановки был установлен.")
                    self.error.emit("Синтез прерван.")
                    self.progress_update.emit(0)

        except asyncio.CancelledError:
             self.log_message.emit("Асинхронная задача синтеза была отменена.")
             self.progress_update.emit(0)
        except Exception as e:
            error_msg = f"Ошибка синтеза: {e}"
            log_error(f"Ошибка в TTSWorker._run_tts: {error_msg}")
            self.error.emit(error_msg)
            self.progress_update.emit(0)
        finally:
             self._current_task = None

    def run(self):
        """Executes the TTS process using asyncio.run()."""
        if not self._is_running:
            print("TTSWorker: Запущен, но сразу остановлен.")
            return
        try:
            asyncio.run(self._run_tts())
        except RuntimeError as e:
            if "cannot call run() while another loop is running" in str(e):
                 error_msg = "Ошибка вложенного запуска asyncio.run()"
                 log_error(error_msg)
                 try: self.error.emit(error_msg)
                 except RuntimeError: print(f"TTSWorker: Ошибка: {error_msg} (сигнал не отправлен)")
            else:
                 error_msg = f"Неожиданная ошибка RuntimeError в потоке TTS: {e}"
                 log_error(f"Ошибка в TTSWorker.run: {error_msg}")
                 try:
                      self.error.emit(error_msg)
                      self.progress_update.emit(0)
                 except RuntimeError: print(f"TTSWorker: Ошибка: {error_msg} (сигнал не отправлен)")
        except Exception as e:
            error_msg = f"Критическая ошибка потока TTS ({type(e).__name__}): {e}"
            log_error(f"Ошибка в TTSWorker.run: {error_msg}")
            try:
                 self.error.emit(error_msg)
                 self.progress_update.emit(0)
            except RuntimeError: print(f"TTSWorker: Ошибка: {error_msg} (сигнал не отправлен)")

    def stop(self):
        """Requests the worker to stop and attempts to cancel the asyncio task."""
        print("TTSWorker: Получен запрос на остановку...")
        self._is_running = False
        if self._current_task and not self._current_task.done():
            print("TTSWorker: Попытка отмены активной asyncio задачи...")
            self._current_task.cancel()

# --- Основной класс GUI (Упрощенный) ---
class EdgeTTSGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.tts_worker = None
        self.voice_loader_thread = None

        self.file_filter = 'All Files (*);;Text Files (*.txt)'
        if DOCX_SUPPORTED:
            self.file_filter += ';;Word Documents (*.docx)'

        self.initUI()

        if not DOCX_SUPPORTED:
            self.log_message("Предупреждение: 'python-docx' не найдена. Чтение .docx недоступно.")

        QTimer.singleShot(100, self.load_voices)

    def initUI(self):
        """Initializes the User Interface."""
        self.setWindowTitle('Text-to-Speech GUI (edge-tts)')
        self.setGeometry(100, 100, 750, 650)
        main_layout = QVBoxLayout(self)

        # --- Section 1: Input Files ---
        input_group_layout = QVBoxLayout()
        input_group_layout.addWidget(QLabel("--- 1. Файлы ---"))
        hbox_text = QHBoxLayout()
        self.lbl_text = QLabel('Файл с текстом:')
        self.le_text_file = QLineEdit(self); self.le_text_file.setPlaceholderText('Выберите файл TXT или DOCX...')
        self.le_text_file.setReadOnly(True)
        self.btn_browse_text = QPushButton('Обзор...')
        self.btn_browse_text.clicked.connect(self.browse_text_file)
        hbox_text.addWidget(self.lbl_text); hbox_text.addWidget(self.le_text_file, 1); hbox_text.addWidget(self.btn_browse_text)
        input_group_layout.addLayout(hbox_text)
        hbox_output = QHBoxLayout()
        self.lbl_output = QLabel('Сохранить как (.mp3):')
        self.le_output_file = QLineEdit(self); self.le_output_file.setPlaceholderText('Укажите путь для сохранения MP3...')
        self.le_output_file.setReadOnly(True)
        self.btn_browse_output = QPushButton('Обзор...')
        self.btn_browse_output.clicked.connect(self.browse_output_file)
        hbox_output.addWidget(self.lbl_output); hbox_output.addWidget(self.le_output_file, 1); hbox_output.addWidget(self.btn_browse_output)
        input_group_layout.addLayout(hbox_output)
        main_layout.addLayout(input_group_layout)

        # --- Section 2: Voice Selection ---
        voice_group_layout = QVBoxLayout()
        voice_group_layout.addWidget(QLabel("--- 2. Голос ---"))
        hbox_voice = QHBoxLayout()
        self.lbl_voice = QLabel('Голос:')
        self.combo_voice = QComboBox(self)
        self.combo_voice_model = QStandardItemModel()
        self.combo_voice.setModel(self.combo_voice_model)
        self.combo_voice.setToolTip("Русские голоса вверху, остальные по алфавиту языка")
        self.combo_voice.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_refresh_voices = QPushButton('Обновить голоса')
        self.btn_refresh_voices.clicked.connect(self.load_voices)
        hbox_voice.addWidget(self.lbl_voice); hbox_voice.addWidget(self.combo_voice, 1); hbox_voice.addWidget(self.btn_refresh_voices)
        voice_group_layout.addLayout(hbox_voice)
        main_layout.addLayout(voice_group_layout)

        # --- Section 3: Audio Settings ---
        settings_group_layout = QVBoxLayout()
        settings_group_layout.addWidget(QLabel("--- 3. Настройки аудио ---"))
        hbox_rate = QHBoxLayout()
        self.lbl_rate = QLabel('Темп:')
        self.slider_rate = QSlider(Qt.Horizontal)
        self.slider_rate.setRange(-100, 100); self.slider_rate.setValue(0)
        self.slider_rate.setTickInterval(10); self.slider_rate.setTickPosition(QSlider.TicksBelow)
        self.lbl_rate_value = QLabel(); self.lbl_rate_value.setMinimumWidth(50)
        self.slider_rate.valueChanged.connect(self.update_rate_label)
        hbox_rate.addWidget(self.lbl_rate); hbox_rate.addWidget(self.slider_rate, 1); hbox_rate.addWidget(self.lbl_rate_value)
        settings_group_layout.addLayout(hbox_rate)
        self.update_rate_label(self.slider_rate.value())
        hbox_volume = QHBoxLayout()
        self.lbl_volume = QLabel('Громкость:')
        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(-100, 100); self.slider_volume.setValue(0)
        self.slider_volume.setTickInterval(10); self.slider_volume.setTickPosition(QSlider.TicksBelow)
        self.lbl_volume_value = QLabel(); self.lbl_volume_value.setMinimumWidth(50)
        self.slider_volume.valueChanged.connect(self.update_volume_label)
        hbox_volume.addWidget(self.lbl_volume); hbox_volume.addWidget(self.slider_volume, 1); hbox_volume.addWidget(self.lbl_volume_value)
        settings_group_layout.addLayout(hbox_volume)
        self.update_volume_label(self.slider_volume.value())
        hbox_pitch = QHBoxLayout()
        self.lbl_pitch = QLabel('Тон:')
        self.slider_pitch = QSlider(Qt.Horizontal)
        self.slider_pitch.setRange(-50, 50); self.slider_pitch.setValue(0)
        self.slider_pitch.setTickInterval(5); self.slider_pitch.setTickPosition(QSlider.TicksBelow)
        self.lbl_pitch_value = QLabel(); self.lbl_pitch_value.setMinimumWidth(50)
        self.slider_pitch.valueChanged.connect(self.update_pitch_label)
        hbox_pitch.addWidget(self.lbl_pitch); hbox_pitch.addWidget(self.slider_pitch, 1); hbox_pitch.addWidget(self.lbl_pitch_value)
        settings_group_layout.addLayout(hbox_pitch)
        self.update_pitch_label(self.slider_pitch.value())
        main_layout.addLayout(settings_group_layout)

        # --- Section 4: Control ---
        control_group_layout = QVBoxLayout()
        control_group_layout.addWidget(QLabel("--- 4. Управление ---"))
        self.btn_start = QPushButton('Начать синтез', self)
        self.btn_start.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; background-color: #4CAF50; color: white; }")
        self.btn_start.clicked.connect(self.start_synthesis)
        control_group_layout.addWidget(self.btn_start)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0); self.progress_bar.setTextVisible(True)
        control_group_layout.addWidget(self.progress_bar)
        main_layout.addLayout(control_group_layout)

        # --- Section 5: Log ---
        log_group_layout = QVBoxLayout()
        self.lbl_status_title = QLabel("--- Лог ---")
        log_group_layout.addWidget(self.lbl_status_title)
        self.status_log = QTextEdit(self)
        self.status_log.setReadOnly(True); self.status_log.setFixedHeight(150)
        log_group_layout.addWidget(self.status_log)
        main_layout.addLayout(log_group_layout)

        self.setLayout(main_layout)
        self._update_ui_state()
        self.show()

    def log_message(self, message):
        if hasattr(self, 'status_log') and self.status_log is not None:
            self.status_log.append(message)
            self.status_log.ensureCursorVisible()
            QApplication.processEvents()
        else:
            print(f"LOG: {message}")

    def show_error(self, title, message):
        full_message = f"{title}: {message}"
        log_error(full_message)
        self.log_message(f"ОШИБКА: {full_message}")
        QMessageBox.critical(self, title, message)

    def load_voices(self):
        if self.voice_loader_thread and self.voice_loader_thread.isRunning():
            self.log_message("Загрузка голосов уже выполняется.")
            return
        self.log_message("Загрузка списка голосов...")
        self.combo_voice_model.clear()
        loading_item = QStandardItem("Загрузка голосов...")
        loading_item.setEnabled(False)
        self.combo_voice_model.appendRow(loading_item)
        self._update_ui_state()
        self.voice_loader_thread = VoiceLoaderThread(self)
        self.voice_loader_thread.voices_loaded.connect(self.on_voices_loaded)
        self.voice_loader_thread.error_occurred.connect(self.on_voice_load_error)
        self.voice_loader_thread.log_message.connect(self.log_message)
        self.voice_loader_thread.finished.connect(self.voice_loader_thread.deleteLater)
        self.voice_loader_thread.finished.connect(lambda: setattr(self, 'voice_loader_thread', None))
        self.voice_loader_thread.start()

    def on_voices_loaded(self, voices):
        self.update_voice_list(voices)
        self._update_ui_state()

    def on_voice_load_error(self, error_message):
        self.show_error("Ошибка загрузки голосов", error_message)
        self.update_voice_list([])
        self.voice_loader_thread = None
        self._update_ui_state()

    def update_voice_list(self, voices):
        self.combo_voice_model.clear()
        preferred_locale = "en-US"
        first_selectable_item = None
        if not voices:
            self.log_message("Голоса не найдены или не удалось загрузить.")
            item = QStandardItem("Нет доступных голосов"); item.setEnabled(False)
            self.combo_voice_model.appendRow(item)
        else:
            voices_by_lang = collections.defaultdict(list)
            for voice in voices:
                locale = voice.get('Locale', 'Unknown Locale')
                voices_by_lang[locale].append(voice)
            for locale in voices_by_lang:
                 voices_by_lang[locale].sort(key=lambda x: x.get('FriendlyName', 'Unknown'))
            ru_voices = voices_by_lang.pop(preferred_locale, None)
            if ru_voices:
                lang_header_item = QStandardItem(f"--- {preferred_locale} ---"); lang_header_item.setEnabled(False)
                self.combo_voice_model.appendRow(lang_header_item)
                for voice in ru_voices:
                    display_name = f"{voice.get('FriendlyName', 'N/A')} ({voice.get('Gender', 'N/A')})"
                    short_name = voice.get('ShortName', 'N/A')
                    voice_item = QStandardItem(display_name); voice_item.setData(short_name, Qt.UserRole)
                    self.combo_voice_model.appendRow(voice_item)
                    if not first_selectable_item: first_selectable_item = voice_item
            other_locales = sorted(voices_by_lang.keys())
            for locale in other_locales:
                lang_header_item = QStandardItem(f"--- {locale} ---"); lang_header_item.setEnabled(False)
                self.combo_voice_model.appendRow(lang_header_item)
                for voice in voices_by_lang[locale]:
                    display_name = f"{voice.get('FriendlyName', 'N/A')} ({voice.get('Gender', 'N/A')})"
                    short_name = voice.get('ShortName', 'N/A')
                    voice_item = QStandardItem(display_name); voice_item.setData(short_name, Qt.UserRole)
                    self.combo_voice_model.appendRow(voice_item)
                    if not first_selectable_item: first_selectable_item = voice_item
            self.log_message(f"Список голосов обновлен ({len(voices)} голосов).")
            self.combo_voice.blockSignals(True)
            selected_index = -1
            if first_selectable_item:
                 index = self.combo_voice_model.indexFromItem(first_selectable_item).row()
                 if index >= 0: selected_index = index
            if selected_index != -1:
                 self.combo_voice.setCurrentIndex(selected_index)
            self.combo_voice.blockSignals(False)
        self._update_ui_state()

    def browse_text_file(self):
        start_dir = os.path.dirname(self.le_text_file.text()) if self.le_text_file.text() else os.path.expanduser("~")
        fname, _ = QFileDialog.getOpenFileName(self, 'Открыть файл с текстом', start_dir, self.file_filter)
        if fname:
            self.le_text_file.setText(fname)
            self.log_message(f"Выбран файл с текстом: {fname}")
            if not self.le_output_file.text():
                 base, _ = os.path.splitext(fname)
                 default_output = base + ".mp3"
                 self.le_output_file.setText(default_output)
                 self.log_message(f"Предложен выходной файл: {default_output}")
            self._update_ui_state()

    def browse_output_file(self):
        default_path = self.le_output_file.text()
        start_dir = os.path.dirname(default_path) if default_path else os.path.expanduser("~")
        default_name = os.path.basename(default_path) if default_path else "output.mp3"
        fname, _ = QFileDialog.getSaveFileName(self, 'Сохранить аудиофайл', os.path.join(start_dir, default_name), 'MP3 Audio (*.mp3);;All Files (*)')
        if fname:
            if not fname.lower().endswith('.mp3'): fname += '.mp3'
            self.le_output_file.setText(fname)
            self.log_message(f"Файл для сохранения аудио: {fname}")
            self._update_ui_state()

    def update_rate_label(self, value):
        self.lbl_rate_value.setText(f"{'+' if value >= 0 else ''}{value}%")

    def update_volume_label(self, value):
        self.lbl_volume_value.setText(f"{'+' if value >= 0 else ''}{value}%")

    def update_pitch_label(self, value):
        self.lbl_pitch_value.setText(f"{'+' if value >= 0 else ''}{value}Hz")

    def read_text_from_file(self, file_path):
        """Reads text content from TXT or DOCX files."""
        _, file_extension = os.path.splitext(file_path); file_extension = file_extension.lower()
        self.log_message(f"Чтение файла: {os.path.basename(file_path)} (тип: {file_extension})")
        try:
            if file_extension == '.txt':
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        return file.read()
                except UnicodeDecodeError:
                    self.log_message("Предупреждение: Файл не в UTF-8, попытка чтения с игнорированием ошибок...")
                    with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
                        return file.read()
            elif file_extension == '.docx':
                if not DOCX_SUPPORTED:
                    raise RuntimeError("Чтение DOCX недоступно: библиотека 'python-docx' не установлена.")
                doc = docx.Document(file_path)
                paragraphs = [para.text.strip() for para in doc.paragraphs if para.text and para.text.strip()]
                full_text = '\n\n'.join(paragraphs)
                if not full_text:
                    self.log_message("Предупреждение: DOCX файл не содержит текстовых параграфов или только пустые строки.")
                return full_text
            else:
                 self.log_message(f"Неизвестный формат {file_extension}, попытка чтения как текст (UTF-8)...")
                 try:
                     with open(file_path, "r", encoding="utf-8", errors='ignore') as file:
                         return file.read()
                 except Exception as e_read:
                      raise RuntimeError(f"Не удалось прочитать файл неизвестного типа '{file_extension}' как текст: {e_read}")
        except Exception as e:
            log_error(f"Ошибка чтения файла {file_path}: {e}")
            raise

    def start_synthesis(self):
        """Starts the text-to-speech synthesis process."""
        if self.tts_worker and self.tts_worker.isRunning():
            self.show_error("Синтез уже идет", "Пожалуйста, дождитесь завершения текущего процесса.")
            return

        text_file = self.le_text_file.text().strip()
        output_file = self.le_output_file.text().strip()
        selected_combo_index = self.combo_voice.currentIndex()

        if not text_file or not os.path.exists(text_file):
            self.show_error("Ошибка ввода", "Выберите существующий файл с текстом.")
            return
        if not output_file:
            self.show_error("Ошибка ввода", "Укажите имя выходного аудиофайла (.mp3).")
            return
        if not output_file.lower().endswith(".mp3"):
             output_file += ".mp3"
             self.le_output_file.setText(output_file)
             self.log_message("Добавлено расширение .mp3 к имени выходного файла.")

        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.isdir(output_dir):
            try:
                os.makedirs(output_dir, exist_ok=True)
                self.log_message(f"Создана выходная директория: {output_dir}")
            except OSError as e:
                self.show_error("Ошибка ввода", f"Не удалось создать директорию для сохранения файла:\n{output_dir}\nОшибка: {e}")
                return

        if selected_combo_index < 0:
             self.show_error("Ошибка ввода", "Голос не выбран.")
             return
        if not self.combo_voice_model or selected_combo_index >= self.combo_voice_model.rowCount():
             self.show_error("Внутренняя ошибка", "Неверный индекс голоса.")
             return
        selected_item = self.combo_voice_model.item(selected_combo_index)
        if not selected_item or not selected_item.isEnabled():
            self.show_error("Ошибка ввода", "Выберите конкретный голос (не заголовок языка).")
            return

        voice_short_name = selected_item.data(Qt.UserRole)
        if not voice_short_name:
             self.show_error("Внутренняя ошибка", "Не удалось получить ShortName для выбранного голоса.")
             return
        voice_full_id = VOICE_MAP.get(voice_short_name)
        if not voice_full_id:
             self.show_error("Внутренняя ошибка", f"Не найден ID (Name) для голоса {voice_short_name} в карте. Попробуйте обновить список голосов.")
             return

        try:
            text_content = self.read_text_from_file(text_file)
            if text_content is None or not text_content.strip():
                self.show_error("Ошибка чтения", f"Файл '{os.path.basename(text_file)}' пуст или не содержит читаемого текста.")
                return
            self.log_message(f"Текст из '{os.path.basename(text_file)}' успешно прочитан ({len(text_content)} симв.).")
        except Exception as e:
            self.show_error("Ошибка чтения файла", f"Не удалось прочитать содержимое файла:\n{e}")
            return

        rate_val = self.slider_rate.value()
        volume_val = self.slider_volume.value()
        pitch_val = self.slider_pitch.value()
        rate_str = f"{'+' if rate_val >= 0 else ''}{rate_val}%"
        volume_str = f"{'+' if volume_val >= 0 else ''}{volume_val}%"
        pitch_str = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"

        self.log_message(f"Запуск синтеза речи (Голос: {voice_short_name})...")
        self.progress_bar.setValue(0)
        self._update_ui_state()

        self.tts_worker = TTSWorker(
            text_content, voice_full_id, output_file,
            rate_str, volume_str, pitch_str,
            parent=self
        )
        self.tts_worker.finished.connect(self.on_tts_finished)
        self.tts_worker.error.connect(self.on_tts_error)
        self.tts_worker.log_message.connect(self.log_message)
        self.tts_worker.progress_update.connect(self.progress_bar.setValue)
        self.tts_worker.finished.connect(self.tts_worker.deleteLater)
        self.tts_worker.error.connect(self.tts_worker.deleteLater)
        self.tts_worker.finished.connect(lambda: setattr(self, 'tts_worker', None))
        self.tts_worker.error.connect(lambda: setattr(self, 'tts_worker', None))
        self.tts_worker.start()

    def on_tts_finished(self, output_path):
        """Handles successful completion of TTS synthesis."""
        self.log_message(f"Синтез успешно завершен! Файл сохранен: {output_path}")
        self.progress_bar.setValue(100)
        # --- ИЗМЕНЕНИЕ: Убираем MessageBox, добавляем звук ---
        # QMessageBox.information(self, "Успех", f"Синтез речи завершен!\nФайл сохранен:\n{output_path}")
        if winsound: # Проверяем, что winsound импортирован (для Windows)
            try:
                winsound.Beep(660, 300) # Воспроизводим звук (частота 660 Гц, длительность 300 мс)
            except Exception as e_sound:
                 self.log_message(f"Предупреждение: Не удалось воспроизвести звук ({e_sound})")
        # --- КОНЕЦ ИЗМЕНЕНИЯ ---
        self._update_ui_state()

    def on_tts_error(self, error_message):
        """Handles errors during TTS synthesis."""
        self.show_error("Ошибка синтеза", f"Произошла ошибка во время синтеза:\n{error_message}")
        self.progress_bar.setValue(0)
        self._update_ui_state()

    def _update_ui_state(self):
        """Updates the enabled/disabled state of UI controls."""
        is_voice_loading = bool(self.voice_loader_thread and self.voice_loader_thread.isRunning())
        is_synthesizing = bool(self.tts_worker and self.tts_worker.isRunning())
        is_busy = is_voice_loading or is_synthesizing

        self.le_text_file.setEnabled(not is_busy)
        self.btn_browse_text.setEnabled(not is_busy)
        self.le_output_file.setEnabled(not is_busy)
        self.btn_browse_output.setEnabled(not is_busy)

        voices_available = False
        if self.combo_voice_model and self.combo_voice_model.rowCount() > 0:
             for i in range(self.combo_voice_model.rowCount()):
                 item = self.combo_voice_model.item(i)
                 if item and item.isEnabled():
                     voices_available = True
                     break
        self.combo_voice.setEnabled(not is_busy and voices_available)
        self.btn_refresh_voices.setEnabled(not is_busy)

        self.slider_rate.setEnabled(not is_busy)
        self.slider_volume.setEnabled(not is_busy)
        self.slider_pitch.setEnabled(not is_busy)

        text_file_ok = bool(self.le_text_file.text().strip() and os.path.exists(self.le_text_file.text().strip()))
        output_file_ok = bool(self.le_output_file.text().strip())
        voice_selected_ok = voices_available and self.combo_voice.currentIndex() >= 0
        voice_is_valid = False
        if voice_selected_ok and self.combo_voice_model:
             current_index = self.combo_voice.currentIndex()
             if 0 <= current_index < self.combo_voice_model.rowCount():
                 current_item = self.combo_voice_model.item(current_index)
                 if current_item:
                     voice_is_valid = current_item.isEnabled()

        can_start = not is_busy and text_file_ok and output_file_ok and voice_selected_ok and voice_is_valid

        self.btn_start.setEnabled(can_start)
        if is_synthesizing:
            self.btn_start.setText("Синтез...")
            self.btn_start.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; background-color: #FF9800; color: white; }")
        elif is_voice_loading:
            self.btn_start.setText("Загрузка голосов...")
            self.btn_start.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; background-color: #FF9800; color: white; }")
        else:
            self.btn_start.setText("Начать синтез")
            if can_start:
                 self.btn_start.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; background-color: #4CAF50; color: white; }")
            else:
                 self.btn_start.setStyleSheet("QPushButton { font-size: 16px; padding: 10px; background-color: #9E9E9E; color: white; }")

    def closeEvent(self, event):
        """Handles the window close event."""
        worker_running = bool(self.tts_worker and self.tts_worker.isRunning())
        loader_running = bool(self.voice_loader_thread and self.voice_loader_thread.isRunning())

        if worker_running or loader_running:
            tasks = []
            if worker_running: tasks.append("Синтез речи")
            if loader_running: tasks.append("Загрузка голосов")
            task_str = " и ".join(tasks)

            reply = QMessageBox.question(self, 'Выход', f"Процесс '{task_str}' еще выполняется. Прервать и выйти?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.log_message("Завершение работы, попытка остановить активные потоки...")
                if worker_running:
                    self.log_message("Остановка потока синтеза...")
                    try:
                        self.tts_worker.stop()
                        if not self.tts_worker.wait(1500):
                             self.log_message("Поток TTS не завершился штатно, принудительное завершение...")
                             self.tts_worker.terminate()
                    except Exception as e: log_error(f"Ошибка остановки потока TTS: {e}")
                if loader_running:
                     self.log_message("Остановка потока загрузки голосов...")
                     try:
                         self.voice_loader_thread.terminate()
                         if not self.voice_loader_thread.wait(500):
                              self.log_message("Поток загрузки голосов не ответил на terminate.")
                     except Exception as e: log_error(f"Ошибка остановки потока загрузки голосов: {e}")
                event.accept()
            else: event.ignore()
        else: event.accept()

# --- Запуск приложения ---
if __name__ == '__main__':
    if sys.platform == "win32":
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            print("INFO: Установлена политика цикла событий WindowsSelectorEventLoopPolicy.")
        except Exception as e_policy:
            print(f"WARNING: Не удалось установить WindowsSelectorEventLoopPolicy: {e_policy}. Используется Proactor.")

    if sys.platform == 'darwin':
        os.environ['OBJC_DISABLE_INITIALIZE_FORK_SAFETY'] = 'YES'

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    app = QApplication(sys.argv)
    ex = EdgeTTSGUI()
    sys.exit(app.exec_())
