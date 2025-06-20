import asyncio
import edge_tts
from pydub import AudioSegment
from pydub.generators import Sine
import os
import re
import uuid
import time
import librosa
import soundfile as sf
import numpy as np
import random
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s')

# Settings
STYLE_SETTINGS = {
    "NORMAL": {"voice": "en-US-AvaNeural", "gain": 0},
    "WHISPER": {"voice": "en-US-AndrewMultilingualNeural", "gain": -10},
    "LOUD": {"voice": "en-US-AriaNeural", "gain": 10},
    "OLD": {"voice": "en-US-ChristopherNeural", "gain": 0},
    "GIRL": {"voice": "en-US-AnaNeural", "gain": 0},
    "GUY": {"voice": "en-US-AndrewMultilingualNeural", "gain": 0},
    "GIRLQ": {"voice": "en-US-AnaNeural", "gain": -20},
    "GIRLW": {"voice": "en-US-AnaNeural", "gain": -30},
}

# Example input
script = """
[[GUY]]I JUST can't believe it! [[GIRL]]However[[PAUSE=1000]][[PAUSE=1000]],[[PAUSE=1000]] I always knew you'd come.
[[OLD]]This[[PAUSE=1000]] is very important. [[NORMAL]]Are you there? [[GIRLW]]But don't worry.
[[WHISPER]]Finally we made it.
"""

def change_pitch(audio, pitch_semitones):
    """
    Changes the pitch of an AudioSegment using librosa.
    :param audio: AudioSegment object
    :param pitch_semitones: Number of semitones to shift the pitch (e.g., -5 for lower, +5 for higher)
    :return: Pitched-shifted AudioSegment
    """
    # Convert AudioSegment to numpy array
    samples = np.array(audio.get_array_of_samples())
    
    # If stereo, librosa expects mono, so take one channel
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))[:, 0]
    
    # Convert to float for librosa
    samples_float = samples.astype(np.float32) / (1 << (audio.sample_width * 8 - 1))
    
    # Apply pitch shift
    pitched_samples = librosa.effects.pitch_shift(
        y=samples_float, sr=audio.frame_rate, n_steps=pitch_semitones
    )
    
    # Convert back to int16 for AudioSegment
    pitched_samples_int = (pitched_samples * (1 << (audio.sample_width * 8 - 1))).astype(samples.dtype)
    
    # Create new AudioSegment
    pitched_audio = AudioSegment(
        pitched_samples_int.tobytes(), 
        frame_rate=audio.frame_rate,
        sample_width=audio.sample_width,
        channels=1 # librosa outputs mono, so we assume mono for now
    )
    
    # If original was stereo, convert back to stereo (by duplicating mono channel)
    if audio.channels == 2:
        pitched_audio = pitched_audio.set_channels(2)
        
    return pitched_audio

def vary_speed(audio, min_rate=0.97, max_rate=1.03):
    """Apply subtle speed variations to make speech less robotic"""
    rate = np.random.uniform(min_rate, max_rate)
    logging.info(f"Applying speed variation with rate {rate:.4f}.")
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * rate)
    }).set_frame_rate(audio.frame_rate)

def add_micro_pauses(audio, probability=0.3, pause_duration=50):
    """Add very short micro-pauses randomly for natural speech rhythm"""
    if random.random() < probability:
        logging.info(f"Adding micro pause of {pause_duration} ms.")
        micro_pause = AudioSegment.silent(duration=pause_duration)
        return audio + micro_pause
    logging.info("No micro pause added.")
    return audio

def apply_natural_volume_variation(audio, variation_range=3):
    """Apply subtle volume variations throughout the audio"""
    # Split audio into small chunks and vary volume slightly
    logging.debug("Applying natural volume variation.")
    chunk_size = 1000  # 1 second chunks
    if len(audio) < chunk_size:
        return audio
    
    varied_audio = AudioSegment.empty()
    
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        # Random volume adjustment within small range
        volume_change = random.uniform(-variation_range, variation_range)
        logging.info(f"Volume change for chunk {i // chunk_size}: {volume_change:.2f} dB.")
        chunk = chunk + volume_change
        varied_audio += chunk
    
    return varied_audio

def add_subtle_emphasis(text):
    """Add subtle emphasis patterns that affect speech naturally"""
    
    # Words that naturally get emphasis in speech
    logging.info("Adding subtle emphasis to text.")
    emphasis_patterns = {
        r'\b(never|always|definitely|absolutely|completely|totally)\b': r'\1[[PAUSE=150]]',
        r'\b(very|really|quite|pretty|so)\s+(\w+)': r'\1 \2[[PAUSE=150]]',  # "very good" gets natural emphasis
        r'\b(but|however|although|though)\b': r'\1[[PAUSE=150]]',  # Transition words
        r'\b(first|second|third|finally|lastly)\b': r'\1[[PAUSE=150]]',  # Sequence words
    }
    
    for pattern, replacement in emphasis_patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        logging.info(f"Applied emphasis pattern: {pattern} -> {replacement}")
    
    logging.info(f"Subtle emphasis added to text: {text}")
    
    return text

def add_natural_sentence_breaks(text):
    """Add natural breaks that humans make in speech"""
    
    # Add slight pauses before certain conjunctions and transitions
    logging.info("Adding natural sentence breaks.")
    transition_words = [
        'but', 'however', 'although', 'meanwhile', 'furthermore', 
        'moreover', 'nevertheless', 'therefore', 'consequently'
    ]
    
    for word in transition_words:
        pattern = r'\b' + word + r'\b'
        replacement = f'[[PAUSE=2000]]{word}'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Add pauses before questions
    # text = re.sub(r'(\w+)(\s*\?)', r'\1[[PAUSE=300]]\2', text)
    
    logging.info(f"Natural sentence breaks added to text: {text}")
    
    return text

def _normalize_pauses_and_punctuation(text):
    """
    Combines consecutive [[PAUSE=XXX]] tags and ensures punctuation appears before the consolidated pause.
    """
    # Step 1: Combine directly adjacent PAUSE tags (and those separated by only whitespace)
    # This needs to be run iteratively until no more combinations are possible.
    while True:
        combined_pause_pattern = re.compile(r"\[\[PAUSE=(\d+)\]\]\s*\[\[PAUSE=(\d+)\]\]")
        
        def combine_pauses_repl(match):
            duration1 = int(match.group(1))
            duration2 = int(match.group(2))
            return f"[[PAUSE={duration1 + duration2}]]"
        
        new_text, num_subs = combined_pause_pattern.subn(combine_pauses_repl, text)
        if num_subs == 0:
            break # No more directly adjacent pauses to combine
        text = new_text

    # Step 2: Iteratively move punctuation that is *after* a PAUSE tag to *before* it,
    # and re-combine pauses if they become adjacent due to the move.
    while True:
        # Pattern: (PAUSE_TAG) + optional_whitespace + (PUNCTUATION)
        # This matches cases like "[[PAUSE=150]]," or "[[PAUSE=150]] ."
        punctuation_after_pause_pattern = re.compile(r"(\[\[PAUSE=\d+\]\])\s*([.,!?;:])")
        
        def move_punctuation_repl(match):
            pause_tag = match.group(1)
            punctuation = match.group(2)
            # Return punctuation followed by a space and the pause tag
            return f"{punctuation} {pause_tag}"
        
        new_text, num_subs = punctuation_after_pause_pattern.subn(move_punctuation_repl, text)
        
        if num_subs == 0:
            break # No more punctuation to move
        
        text = new_text
        
        # After moving punctuation, re-run the combine adjacent pauses step
        # in case moving punctuation made pauses adjacent (e.g., ", [[PAUSE=150]][[PAUSE=1000]]")
        while True:
            combined_pause_pattern_inner = re.compile(r"\[\[PAUSE=(\d+)\]\]\s*\[\[PAUSE=(\d+)\]\]")
            def combine_pauses_repl_inner(match):
                duration1 = int(match.group(1))
                duration2 = int(match.group(2))
                return f"[[PAUSE={duration1 + duration2}]]"
            new_text_inner, num_subs_inner = combined_pause_pattern_inner.subn(combine_pauses_repl_inner, text)
            if num_subs_inner == 0:
                break
            text = new_text_inner

    # Final cleanup of extra spaces
    normalized_text = re.sub(r'\s+', ' ', text).strip()
    
    logging.info(f"Normalized pauses and punctuation: {normalized_text}")
    
    return normalized_text

def enhance_audio_naturalness(input_file, output_file):
    """Post-process audio to make it sound more natural"""
    
    # Load audio
    y, sr = librosa.load(input_file, sr=None)
    
    # Method 1: Apply subtle random pitch variations frame by frame
    # This creates more natural-sounding speech
    frame_length = 2048
    hop_length = 512
    
    # Process audio in chunks to avoid memory issues
    enhanced_audio = []
    
    for i in range(0, len(y), hop_length * 100):  # Process in larger chunks
        chunk_end = min(i + hop_length * 100, len(y))
        chunk = y[i:chunk_end]
        
        # Apply subtle pitch variation (random but small)
        pitch_variation = np.random.uniform(-0.3, 0.3)  # Small random pitch shift
        try:
            chunk_shifted = librosa.effects.pitch_shift(
                chunk, sr=sr, n_steps=pitch_variation, bins_per_octave=12
            )
        except:
            # If pitch shift fails, use original chunk
            chunk_shifted = chunk
            
        enhanced_audio.append(chunk_shifted)
    
    # Combine all chunks
    y_shifted = np.concatenate(enhanced_audio)
    
    # Ensure same length as original (truncate if needed)
    if len(y_shifted) > len(y):
        y_shifted = y_shifted[:len(y)]
    elif len(y_shifted) < len(y):
        # Pad with zeros if shorter
        padding = len(y) - len(y_shifted)
        y_shifted = np.pad(y_shifted, (0, padding), mode='constant')
    
    # Add very subtle background noise (makes it less "digital") - Temporarily disabled for clearer tracking
    noise_level = 0.0 # Set to 0 to disable noise
    noise = np.random.normal(0, noise_level, len(y_shifted))
    y_natural = y_shifted + noise
    
    # Apply gentle compression and normalize
    y_compressed = librosa.util.normalize(y_natural) * 0.95
    
    # Save enhanced audio
    sf.write(output_file, y_compressed, sr)
    print(f"Enhanced audio saved as: {output_file}")

def enhance_audio_naturalness_simple(input_file, output_file):
    """Simplified version with consistent pitch shift"""
    
    # Load audio
    y, sr = librosa.load(input_file, sr=None)
    
    # Apply a single, subtle pitch variation
    pitch_shift_amount = np.random.uniform(-0.2, 0.2)  # Very subtle
    
    try:
        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=pitch_shift_amount)
        print("Pitch shift amount:", pitch_shift_amount)
    except:
        print("Pitch shift failed, using original audio")
        y_shifted = y
    
    # Add very subtle background noise - Temporarily disabled for clearer tracking
    noise_level = 0.0 # Set to 0 to disable noise
    noise = np.random.normal(0, noise_level, len(y_shifted))
    print("Noise level:", noise_level)
    y_natural = y_shifted + noise
    
    # Normalize
    y_final = librosa.util.normalize(y_natural) * 0.95
    
    # Save enhanced audio
    sf.write(output_file, y_final, sr)
    print(f"Enhanced audio saved as: {output_file}")

def humanize_text(text):
    """Preprocess text to sound more natural when spoken - NO SSML"""
    logging.info(f"\n--- Text entering humanize_text: ---\n{text}")
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Add natural spacing after punctuation for better speech flow
    text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([,;:])([a-zA-Z])', r'\1 \2', text)
    
    # Convert contractions to more natural speech
    contractions = {
        "don't": "do not", "won't": "will not", "can't": "cannot",
        "shouldn't": "should not", "wouldn't": "would not",
        "couldn't": "could not", "isn't": "is not", "aren't": "are not",
        "wasn't": "was not", "weren't": "were not", "hasn't": "has not",
        "haven't": "have not", "hadn't": "had not"
    }
    
    for contraction, expansion in contractions.items():
        text = re.sub(r'\b' + contraction + r'\b', expansion, text, flags=re.IGNORECASE)
    
    # Add subtle emphasis patterns
    text = add_subtle_emphasis(text)
    
    # Add natural sentence breaks
    text = add_natural_sentence_breaks(text)
    
    # Normalize pauses and punctuation
    text = _normalize_pauses_and_punctuation(text)

    # Convert ellipses to more natural pauses
    # text = re.sub(r'\.\.\.', '[[PAUSE=800]]...', text) # Removed as EdgeTTS handles "..." naturally
    
    logging.info(f"--- Text after humanize_text: ---\n{text}")
    return text

def add_natural_pauses(text):
    """Add natural pauses using your existing PAUSE system"""
    
    # Add pauses after certain punctuation
    text = re.sub(r'([.!?])\s+', r'\1 [[PAUSE=500]] ', text)
    text = re.sub(r'([,;:])\s+', r'\1 [[PAUSE=250]] ', text)
    
    # Add longer pauses for ellipses
    # text = re.sub(r'\.\.\.', '[[PAUSE=800]]...', text)
    
    return text

def parse_script(text):
    logging.info("Parsing script.")
    current_style = "NORMAL"
    current_pitch = 0
    tokens = []

    # First, apply humanization to the entire text
    # This ensures that any [[PAUSE=XXX]] tags introduced by humanization
    # are present before splitting the text into parts.
    humanized_full_text = humanize_text(text)
    logging.info(f"\n--- Humanized Full Text before splitting: ---\n{humanized_full_text}")

    parts = re.split(r"(\[\[.*?\]\])", humanized_full_text.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Handle pause command (case-insensitive for 'pause')
        if re.match(r"\[\[(PAUSE|pause)=\d+\]\]", part):
            pause_duration = int(re.findall(r"\d+", part)[0])
            tokens.append(("SILENCE", pause_duration, 0, current_style))

        # Handle pitch shift
        elif re.match(r"\[\[PITCH=[+-]?\d+\]\]", part):
            current_pitch = int(re.findall(r"[+-]?\d+", part)[0])

        # Handle voice/style switch
        elif re.match(r"\[\[[A-Z]+\]\]", part):
            tag = part.strip("[]")
            if tag in STYLE_SETTINGS:
                current_style = tag

        # Text — these parts are already humanized from humanized_full_text
        else:
            # No need to call humanize_text here again, as it's done on the full text
            # Optionally add natural pauses using your pause system if needed
            # enhanced_text = add_natural_pauses(part) # if add_natural_pauses is not part of humanize_text
            
            tokens.append(("SPEECH", part, current_pitch, current_style))

    return tokens

async def save_tts_with_retries(text, voice, out_file, max_retries=3):
    base_wait = 1  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            # Use simple text without any SSML markup
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(out_file)
            logging.info(f"Text: {text}")
            logging.info(f"Voice: {voice}")
            logging.info(f"Output file: {out_file}")
            return  # success, exit
        except Exception as e:
            print(f"Warning: attempt {attempt} failed with error: {e}")
            if attempt == max_retries:
                raise
            wait_time = base_wait * (2 ** (attempt - 1))  # exponential backoff: 1s, 2s, 4s...
            print(f"Retrying after {wait_time}s...")
            await asyncio.sleep(wait_time)

# Dynamic rate limiting variables
MIN_DELAY_BETWEEN_REQUESTS = 1.0  # seconds
_last_request_time = 0

async def generate_audio(chunks):
    global _last_request_time
    audio_files_for_combination = [] # This list will contain only the final chunk files for combination
    all_temp_files_for_cleanup = [] # This list will contain ALL temporary files created
    previous_was_speech = False
    
    for i, (chunk_type, content, pitch, style) in enumerate(chunks):
        chunk_id = f"chunk_{i:02d}_{uuid.uuid4().hex[:6]}" # Unique ID for this chunk

        if chunk_type == "SILENCE":
            silence_duration = content
            
            # Occasionally add breathing sounds during longer pauses
            if silence_duration > 800 and random.random() < 0.4:  # 40% chance for long pauses
                silence = AudioSegment.silent(duration=silence_duration - 300)
                final_silence = silence
            else:
                final_silence = AudioSegment.silent(duration=silence_duration)
            
            silence_file = f"audio/{chunk_id}_silence.mp3"
            final_silence.export(silence_file, format="mp3")
            audio_files_for_combination.append(silence_file) # Add to list for final combination
            all_temp_files_for_cleanup.append(silence_file) # Add to cleanup list
        else:
            voice = STYLE_SETTINGS[style]["voice"]
            gain = STYLE_SETTINGS[style]["gain"]

            # Rate limiting: wait if last request was too recent
            now = time.time()
            elapsed = now - _last_request_time
            if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
                wait = MIN_DELAY_BETWEEN_REQUESTS - elapsed
                logging.info(f"Rate limiting: waiting {wait:.2f}s before next TTS call")
                await asyncio.sleep(wait)

            raw_tts_file = f"audio/{chunk_id}_raw_tts.mp3"
            logging.info(f"Processing chunk {i+1}: Type={chunk_type}, Content='{content}', Pitch={pitch}, Style='{style}'")
            await save_tts_with_retries(content, voice, raw_tts_file)
            _last_request_time = time.time()
            all_temp_files_for_cleanup.append(raw_tts_file) # Add to cleanup list

            # Check if the generated TTS file is empty
            if not os.path.exists(raw_tts_file) or os.path.getsize(raw_tts_file) == 0:
                logging.error(f"Generated TTS file is empty or does not exist: {raw_tts_file}. Content: '{content}'")
                # Depending on desired behavior, could raise an error, skip, or retry
                continue # Skip this chunk if the file is empty

            audio = AudioSegment.from_file(raw_tts_file)
            logging.info(f"Saved raw TTS for {chunk_id} to {raw_tts_file}")
            
            # Apply gain adjustment
            if gain != 0:
                audio += gain
                gain_adjusted_file = f"audio/{chunk_id}_gain_adjusted.mp3"
                audio.export(gain_adjusted_file, format="mp3")
                logging.info(f"Saved gain adjusted audio for {chunk_id} to {gain_adjusted_file}")
                all_temp_files_for_cleanup.append(gain_adjusted_file) # Add to cleanup list
            
            # Apply pitch changes
            if pitch != 0:
                audio = change_pitch(audio, pitch)
                pitch_adjusted_file = f"audio/{chunk_id}_pitch_adjusted.mp3"
                audio.export(pitch_adjusted_file, format="mp3")
                logging.info(f"Saved pitch adjusted audio for {chunk_id} to {pitch_adjusted_file}")
                all_temp_files_for_cleanup.append(pitch_adjusted_file) # Add to cleanup list
            
            # HUMANIZATION ENHANCEMENTS
            
            # 1. Apply speed variation for naturalness
            audio = vary_speed(audio, min_rate=0.97, max_rate=1.03)
            speed_varied_file = f"audio/{chunk_id}_speed_varied.mp3"
            audio.export(speed_varied_file, format="mp3")
            logging.info(f"Saved speed varied audio for {chunk_id} to {speed_varied_file}")
            all_temp_files_for_cleanup.append(speed_varied_file) # Add to cleanup list
            
            # 2. Add subtle volume variations
            audio = apply_natural_volume_variation(audio, variation_range=3)
            volume_varied_file = f"audio/{chunk_id}_volume_varied.mp3"
            audio.export(volume_varied_file, format="mp3")
            logging.info(f"Saved volume varied audio for {chunk_id} to {volume_varied_file}")
            all_temp_files_for_cleanup.append(volume_varied_file) # Add to cleanup list
            
            # 3. Add micro-pauses occasionally
            original_len = len(audio)
            audio = add_micro_pauses(audio, probability=0.3)
            if len(audio) > original_len: # Only save if a pause was actually added
                micro_paused_file = f"audio/{chunk_id}_micro_paused.mp3"
                audio.export(micro_paused_file, format="mp3")
                logging.info(f"Saved micro paused audio for {chunk_id} to {micro_paused_file}")
                all_temp_files_for_cleanup.append(micro_paused_file) # Add to cleanup list
            
            # Final chunk output for combination
            final_chunk_file = f"audio/{chunk_id}_final_chunk.mp3"
            audio.export(final_chunk_file, format="mp3")
            audio_files_for_combination.append(final_chunk_file)
            all_temp_files_for_cleanup.append(final_chunk_file) # Add to cleanup list
            previous_was_speech = True

    return audio_files_for_combination, all_temp_files_for_cleanup

def combine_and_cleanup(audio_files_for_combination, all_temp_files_for_cleanup, original_output="final_output_original.mp3", enhanced_output="final_output_enhanced.mp3"):
    final = AudioSegment.empty()
    
    for i, f in enumerate(audio_files_for_combination):
        audio = AudioSegment.from_file(f)
        
        # Add subtle crossfade between chunks for smoother transitions
        if i > 0 and len(audio) > 100:  # Only crossfade if audio is long enough
            crossfade_duration = min(50, len(audio) // 4)  # Max 50ms crossfade
            final = final.append(audio, crossfade=crossfade_duration)
        else:
            final += audio
            
    # Save combined audio before final humanization touches
    original_output = "audio/audio_final_combined.mp3"
    final = final.normalize(headroom=0.1)

    final.export(original_output, format="mp3")
    logging.info(f"Saved combined audio to {original_output}")

    # Apply final humanization touches
    
    # 1. Normalize audio levels but preserve dynamics
    
    # 2. Add very subtle background ambience (optional) - Temporarily disabled for clearer tracking
    # if len(final) > 5000:  # Only for longer audio
    #     # Create very quiet pink noise
    #     ambience_level = -45  # Very quiet
    #     pink_noise = AudioSegment.silent(duration=len(final))
        
    #     # Simulate pink noise with multiple sine waves
    #     for freq in [50, 100, 200, 400, 800]:
    #         component = Sine(freq).to_audio_segment(duration=len(final)) + ambience_level
    #         pink_noise = pink_noise.overlay(component)
        
    #     # Mix with original audio
    #     final = final.overlay(pink_noise)
    
    # Save original combined audio (now includes normalization)

    print(f"✅ Original combined audio saved as: {original_output}")

    # Try enhanced version, fall back to simple if it fails
    # try:
    #     # Temporarily disable noise in enhancement functions for clearer tracking
    #     enhance_audio_naturalness_simple(original_output, enhanced_output)
    #     print(f"✅ Enhanced audio saved as: {enhanced_output}")
    # except Exception as e:
    #     print(f"Warning: Audio enhancement failed: {e}")
    #     print("Using original audio without enhancement")

    logging.info("--- Starting temporary file cleanup ---")
    logging.info(f"Files to clean up: {all_temp_files_for_cleanup}")
    # Clean up temporary chunk files after all processing is done
    for f in all_temp_files_for_cleanup:
        if os.path.exists(f):
            try:
                os.remove(f)
                logging.debug(f"Cleaned up temporary file: {f}")
            except Exception as e:
                logging.error(f"Error cleaning up temporary file {f}: {e}")
        else:
            logging.debug(f"Temporary file not found (already removed or never created): {f}")
    
    remaining_files = os.listdir('audio')
    logging.debug(f"Files remaining in audio/ directory after cleanup: {remaining_files}")

async def main():
    # Ensure audio output directory exists
    os.makedirs('audio', exist_ok=True)
    logging.debug("--- Initial Script Text ---")
    logging.debug(script)
    logging.debug("---------------------------")
    logging.debug("Parsing script...")
    parsed_chunks = parse_script(script)
    logging.debug(f"Found {len(parsed_chunks)} chunks")
    logging.debug("\n--- Parsed Chunks (Tokens) ---")
    for chunk in parsed_chunks:
        logging.debug(chunk)
    logging.debug("------------------------------")
    
    logging.debug("Generating audio...")
    audio_files_for_combination, all_temp_files_for_cleanup = await generate_audio(parsed_chunks)
    
    print("Combining and processing...")
    combine_and_cleanup(audio_files_for_combination, all_temp_files_for_cleanup)
    
    print("✅ Complete!")

if __name__ == "__main__":
    asyncio.run(main())
