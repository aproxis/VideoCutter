# voice_generator.py - Edge TTS voice generation
import edge_tts
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VoiceGenerator:
    def __init__(self, config):
        self.config = config
        self.voice = config.tts_voice
        self.rate = config.tts_rate
        self.volume = config.tts_volume
        logger.info("VoiceGenerator initialized.")
    
    def generate_audio(self, text, output_path):
        """Generate audio from text using Edge TTS"""
        logger.info(f"Generating voiceover for text of length {len(text)} to {output_path}...")
        try:
            asyncio.run(self._generate_audio_async(text, output_path))
            logger.info(f"Generated voiceover: {output_path}")
        except Exception as e:
            logger.error(f"Error generating voiceover to {output_path}: {str(e)}", exc_info=True)
    
    async def _generate_audio_async(self, text, output_path):
        """Async audio generation"""
        communicate = edge_tts.Communicate(
            text, 
            self.voice, 
            rate=self.rate, 
            volume=self.volume
        )
        
        await communicate.save(str(output_path))
    
    def list_voices(self):
        """List available voices"""
        logger.info("Listing available Edge TTS voices...")
        voices = asyncio.run(self._list_voices_async())
        logger.info(f"Found {len(voices)} Edge TTS voices.")
        return voices
    
    async def _list_voices_async(self):
        """Get list of available voices"""
        voices = await edge_tts.list_voices()
        return voices
