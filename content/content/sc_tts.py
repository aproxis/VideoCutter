from speechcraft import text2voice
from media_toolkit import AudioFile
import os

# simple text2speech synthesis
text = "I love society [laughs]! [happy] What a day to make voice overs with artificial intelligence."
audio_numpy, sample_rate = text2voice(text, voice="en_speaker_3")

# Define the output filename
output_filename = "generated_speech.wav"
# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the full output path
output_path = os.path.join(script_dir, output_filename)

# Save the audio
try:
    audio = AudioFile().from_np_array(audio_numpy, sr=sample_rate)
    audio.save(output_path)
    print(f"Audio saved successfully to: {output_path}")
except Exception as e:
    print(f"Error saving audio: {e}")
