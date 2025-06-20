tts = StandaloneTTSPipeline()
audio, sr, path = tts.process_text_direct(
    text="Your text with [laughs] and EMPHASIS!",
    filename="my_audio.wav"
)