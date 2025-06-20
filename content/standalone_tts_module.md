1. Independent Initialization
python# Works completely on its own
tts_pipeline = StandaloneTTSPipeline(
    default_speaker="en_speaker_3",
    output_dir="tts_output"
)
2. Direct TTS Processing
python# No external dependencies needed
audio_data, sr, path = tts_pipeline.process_text_direct(
    text="Hello! [laughs] This works independently!",
    voice="en_speaker_3"
)
3. Comprehensive Voice Management
python# List all available voices
tts_pipeline.list_voices("english")

# Create voice clones
tts_pipeline.create_voice_clone("sample.wav", "my_voice")
🔗 Easy Integration with Your OpenAI Processor:
Option 1: Use External Rewriter Function
python# Your existing rewrite function
def my_openai_rewriter(text):
    # Your OpenAI logic here
    return rewritten_text

# Use with TTS pipeline
rewritten, audio, sr, path = tts_pipeline.process_with_external_rewriter(
    original_text="Your script here",
    rewrite_function=my_openai_rewriter,
    voice="en_speaker_3"
)
Option 2: Get Optimized Prompt for Your System
python# Get the SpeechCraft-optimized prompt
optimized_prompt = tts_pipeline.get_youtube_prompt()

# Use in your existing TranscriptProcessor
your_processor.config.rewrite_prompt = optimized_prompt
rewritten = your_processor.rewrite_transcript(original_text)

# Then generate TTS
audio_data, sr, path = tts_pipeline.process_text_direct(rewritten)
🎯 Key Advantages:

✅ Completely Independent - No dependencies on your OpenAI code
✅ Easy Integration - Can work with any text processing function
✅ Full SpeechCraft Support - All accents and expressions included
✅ Voice Cloning Ready - Built-in voice embedding creation
✅ Comprehensive Logging - Track all TTS operations
✅ Flexible Output - Configurable file paths and formats

🚀 Quick Start:
pythonfrom standalone_tts import StandaloneTTSPipeline

# Initialize
tts = StandaloneTTSPipeline()

# Show accent guide
tts.show_accent_guide()

# Generate TTS
audio, sr, path = tts.process_text_direct(
    text="Your text with [laughs] and EMPHASIS!",
    filename="my_audio.wav"
)