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

# Settings
STYLE_SETTINGS = {
    "NORMAL": {"voice": "en-US-AvaNeural", "gain": 0},
    "WHISPER": {"voice": "en-US-AndrewMultilingualNeural", "gain": -10},
    "LOUD": {"voice": "en-US-AriaNeural", "gain": 10},
    "OLD": {"voice": "en-US-ChristopherNeural", "gain": 0},
    "GIRL": {"voice": "en-US-AnaNeural", "gain": 0},
    "GUY": {"voice": "en-US-AndrewMultilingualNeural", "gain": -10},
    "GIRLLL": {"voice": "en-US-AnaNeural", "gain": -20},
    "GIRLLLL": {"voice": "en-US-AnaNeural", "gain": -30},
}

# Example input
script = """
I can't believe it! However, I always knew you'd come.
This is very important. But don't worry.
Finally we made it.
"""

def vary_speed(audio, min_rate=0.97, max_rate=1.03):
    """Apply subtle speed variations to make speech less robotic"""
    rate = np.random.uniform(min_rate, max_rate)
    return audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate * rate)
    }).set_frame_rate(audio.frame_rate)

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

def create_breath_sound(duration_ms=300, volume_reduction=25):
    """Generate a subtle breath sound"""
    # Create a soft noise-like breath sound
    breath_freq = 200  # Low frequency for breath-like sound
    breath = Sine(breath_freq).to_audio_segment(duration=duration_ms)
    
    # Add some noise characteristics
    # Create pink noise-like effect by mixing multiple frequencies
    for freq in [150, 180, 220, 250]:
        component = Sine(freq).to_audio_segment(duration=duration_ms) - (volume_reduction + 10)
        breath = breath.overlay(component)
    
    # Fade in and out for naturalness
    breath = breath.fade_in(50).fade_out(50)
    
    # Reduce volume significantly
    breath = breath - volume_reduction
    
    return breath

def add_micro_pauses(audio, probability=0.3, pause_duration=50):
    """Add very short micro-pauses randomly for natural speech rhythm"""
    if random.random() < probability:
        micro_pause = AudioSegment.silent(duration=pause_duration)
        return audio + micro_pause
    return audio

def apply_natural_volume_variation(audio, variation_range=3):
    """Apply subtle volume variations throughout the audio"""
    # Split audio into small chunks and vary volume slightly
    chunk_size = 1000  # 1 second chunks
    if len(audio) < chunk_size:
        return audio
    
    varied_audio = AudioSegment.empty()
    
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i + chunk_size]
        # Random volume adjustment within small range
        volume_change = random.uniform(-variation_range, variation_range)
        chunk = chunk + volume_change
        varied_audio += chunk
    
    return varied_audio

def add_subtle_emphasis(text):
    """Add subtle emphasis patterns that affect speech naturally"""
    
    # Words that naturally get emphasis in speech
    emphasis_patterns = {
        r'\b(never|always|definitely|absolutely|completely|totally)\b': r'\1',
        r'\b(very|really|quite|pretty|so)\s+(\w+)': r'\1 \2',  # "very good" gets natural emphasis
        r'\b(but|however|although|though)\b': r'\1',  # Transition words
        r'\b(first|second|third|finally|lastly)\b': r'\1',  # Sequence words
    }
    
    for pattern, replacement in emphasis_patterns.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    return text

def add_natural_sentence_breaks(text):
    """Add natural breaks that humans make in speech"""
    
    # Add slight pauses before certain conjunctions and transitions
    transition_words = [
        'but', 'however', 'although', 'meanwhile', 'furthermore', 
        'moreover', 'nevertheless', 'therefore', 'consequently'
    ]
    
    for word in transition_words:
        pattern = r'\b' + word + r'\b'
        replacement = f'[[PAUSE=200]]{word}'
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    
    # Add pauses before questions
    text = re.sub(r'(\w+)(\s*\?)', r'\1[[PAUSE=300]]\2', text)
    
    return text

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
    
    # Add very subtle background noise (makes it less "digital")
    noise_level = 0.001
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
    except:
        print("Pitch shift failed, using original audio")
        y_shifted = y
    
    # Add very subtle background noise
    noise_level = 0.0005
    noise = np.random.normal(0, noise_level, len(y_shifted))
    y_natural = y_shifted + noise
    
    # Normalize
    y_final = librosa.util.normalize(y_natural) * 0.95
    
    # Save enhanced audio
    sf.write(output_file, y_final, sr)
    print(f"Enhanced audio saved as: {output_file}")

def humanize_text(text):
    """Preprocess text to sound more natural when spoken - NO SSML"""
    
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
    
    # Convert ellipses to more natural pauses
    text = re.sub(r'\.\.\.', '[[PAUSE=800]]...', text)
    
    return text

def add_natural_pauses(text):
    """Add natural pauses using your existing PAUSE system"""
    
    # Add pauses after certain punctuation
    text = re.sub(r'([.!?])\s+', r'\1 [[PAUSE=500]] ', text)
    text = re.sub(r'([,;:])\s+', r'\1 [[PAUSE=250]] ', text)
    
    # Add longer pauses for ellipses
    text = re.sub(r'\.\.\.', '[[PAUSE=800]]...', text)
    
    return text

def parse_script(text):
    current_style = "NORMAL"
    current_pitch = 0
    tokens = []

    parts = re.split(r"(\[\[.*?\]\])", text.strip())

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Handle pause command
        if re.match(r"\[\[PAUSE=\d+\]\]", part):
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

        # Text — include ellipses as-is, but enhance for naturalness
        else:
            # Apply text humanization (no SSML, just clean text)
            enhanced_text = humanize_text(part)
            
            # Optionally add natural pauses using your pause system
            # enhanced_text = add_natural_pauses(enhanced_text)
            
            tokens.append(("SPEECH", enhanced_text, current_pitch, current_style))

    return tokens

async def save_tts_with_retries(text, voice, out_file, max_retries=3):
    base_wait = 1  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            # Use simple text without any SSML markup
            communicate = edge_tts.Communicate(text=text, voice=voice)
            await communicate.save(out_file)
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
    audio_files = []
    previous_was_speech = False
    
    for i, (chunk_type, content, pitch, style) in enumerate(chunks):
        file = f"{uuid.uuid4()}.mp3"

        if chunk_type == "SILENCE":
            silence_duration = content
            
            # Occasionally add breathing sounds during longer pauses
            if silence_duration > 800 and random.random() < 0.4:  # 40% chance for long pauses
                silence = AudioSegment.silent(duration=silence_duration - 300)
                breath = create_breath_sound(duration_ms=300, volume_reduction=25)
                final_silence = silence + breath
            else:
                final_silence = AudioSegment.silent(duration=silence_duration)
            
            final_silence.export(file, format="mp3")
        else:
            voice = STYLE_SETTINGS[style]["voice"]
            gain = STYLE_SETTINGS[style]["gain"]

            # Rate limiting: wait if last request was too recent
            now = time.time()
            elapsed = now - _last_request_time
            if elapsed < MIN_DELAY_BETWEEN_REQUESTS:
                wait = MIN_DELAY_BETWEEN_REQUESTS - elapsed
                print(f"Rate limiting: waiting {wait:.2f}s before next TTS call")
                await asyncio.sleep(wait)

            await save_tts_with_retries(content, voice, file)
            _last_request_time = time.time()

            audio = AudioSegment.from_file(file)
            
            # Apply gain adjustment
            if gain != 0:
                audio += gain
            
            # Apply pitch changes
            if pitch != 0:
                audio = change_pitch(audio, pitch)
            
            # HUMANIZATION ENHANCEMENTS
            
            # 1. Apply speed variation for naturalness
            audio = vary_speed(audio, min_rate=0.97, max_rate=1.03)
            
            # 2. Add subtle volume variations
            audio = apply_natural_volume_variation(audio, variation_range=2)
            
            # 3. Add micro-pauses occasionally
            audio = add_micro_pauses(audio, probability=0.2)
            
            # 4. Add breathing between speech chunks occasionally
            if previous_was_speech and random.random() < 0.15:  # 15% chance
                breath = create_breath_sound(duration_ms=200, volume_reduction=30)
                audio = breath + audio
            
            audio.export(file, format="mp3")
            previous_was_speech = True

        audio_files.append(file)
    return audio_files

def combine_and_cleanup(files, original_output="final_output_original.mp3", enhanced_output="final_output_enhanced.mp3"):
    final = AudioSegment.empty()
    
    for i, f in enumerate(files):
        audio = AudioSegment.from_file(f)
        
        # Add subtle crossfade between chunks for smoother transitions
        if i > 0 and len(audio) > 100:  # Only crossfade if audio is long enough
            crossfade_duration = min(50, len(audio) // 4)  # Max 50ms crossfade
            final = final.append(audio, crossfade=crossfade_duration)
        else:
            final += audio
            
        os.remove(f)
    
    # Apply final humanization touches
    
    # 1. Normalize audio levels but preserve dynamics
    final = final.normalize(headroom=0.1)
    
    # 2. Add very subtle background ambience (optional)
    if len(final) > 5000:  # Only for longer audio
        # Create very quiet pink noise
        ambience_level = -45  # Very quiet
        pink_noise = AudioSegment.silent(duration=len(final))
        
        # Simulate pink noise with multiple sine waves
        for freq in [50, 100, 200, 400, 800]:
            component = Sine(freq).to_audio_segment(duration=len(final)) + ambience_level
            pink_noise = pink_noise.overlay(component)
        
        # Mix with original audio
        final = final.overlay(pink_noise)
    
    # Save original combined audio
    final.export(original_output, format="mp3")
    print(f"✅ Original combined audio saved as: {original_output}")

    # Try enhanced version, fall back to simple if it fails
    try:
        enhance_audio_naturalness_simple(original_output, enhanced_output)
        print(f"✅ Enhanced audio saved as: {enhanced_output}")
    except Exception as e:
        print(f"Warning: Audio enhancement failed: {e}")
        print("Using original audio without enhancement")

async def main():
    print("Parsing script...")
    parsed_chunks = parse_script(script)
    print(f"Found {len(parsed_chunks)} chunks")
    
    print("Generating audio...")
    audio_files = await generate_audio(parsed_chunks)
    
    print("Combining and processing...")
    combine_and_cleanup(audio_files)
    
    print("✅ Complete!")

if __name__ == "__main__":
    asyncio.run(main())
