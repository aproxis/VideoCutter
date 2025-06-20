import os
import logging
from typing import Optional, Tuple
import numpy as np
from speechcraft import text2voice, voice2embedding
from media_toolkit import AudioFile

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechCraftTTS:
    """
    SpeechCraft TTS wrapper with support for voice cloning and accent generation
    """
    
    def __init__(self, default_speaker: str = "en_speaker_3"):
        """
        Initialize SpeechCraft TTS
        
        Args:
            default_speaker: Default speaker voice to use
        """
        self.default_speaker = default_speaker
        self.voice_embeddings = {}  # Cache for voice embeddings
        logger.info("SpeechCraftTTS initialized")
    
    def create_voice_embedding(self, audio_file_path: str, voice_name: str) -> str:
        """
        Create voice embedding from audio sample for voice cloning
        
        Args:
            audio_file_path: Path to audio sample (7-15 seconds recommended)
            voice_name: Name to save the embedding as
            
        Returns:
            Voice embedding identifier
        """
        try:
            logger.info(f"Creating voice embedding '{voice_name}' from {audio_file_path}")
            embedding = voice2embedding(
                audio_file=audio_file_path, 
                voice_name=voice_name
            ).save_to_speaker_lib()
            
            self.voice_embeddings[voice_name] = embedding
            logger.info(f"Voice embedding '{voice_name}' created successfully")
            return voice_name
            
        except Exception as e:
            logger.error(f"Failed to create voice embedding: {e}")
            raise
    
    def generate_tts(
        self, 
        text: str, 
        voice: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> Tuple[np.ndarray, int]:
        """
        Generate TTS audio from text
        
        Args:
            text: Text to convert to speech (with SpeechCraft accents)
            voice: Voice to use (speaker name or embedding name)
            output_path: Optional path to save audio file
            
        Returns:
            Tuple of (audio_numpy_array, sample_rate)
        """
        try:
            # Use provided voice or default speaker
            speaker_voice = voice or self.default_speaker
            
            logger.info(f"Generating TTS with voice: {speaker_voice}")
            logger.info(f"Text length: {len(text)} characters")
            
            # Generate TTS
            if speaker_voice in self.voice_embeddings:
                # Use voice embedding
                audio_numpy, sample_rate = text2voice(
                    text, 
                    voice=self.voice_embeddings[speaker_voice]
                )
            else:
                # Use speaker name (passed as 'voice' argument)
                audio_numpy, sample_rate = text2voice(
                    text, 
                    voice=speaker_voice
                )
            
            logger.info(f"TTS generated successfully. Sample rate: {sample_rate}")
            
            # Save audio if output path provided
            if output_path:
                self.save_audio(audio_numpy, sample_rate, output_path)
            
            return audio_numpy, sample_rate
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise
    
    def save_audio(self, audio_numpy: np.ndarray, sample_rate: int, output_path: str):
        """
        Save audio numpy array to file
        
        Args:
            audio_numpy: Audio data as numpy array
            sample_rate: Audio sample rate
            output_path: Path to save the audio file
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert and save using media-toolkit
            audio = AudioFile().from_np_array(audio_numpy, sr=sample_rate)
            audio.save(output_path)
            
            logger.info(f"Audio saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise

class SpeechCraftPromptGenerator:
    """
    Generate prompts optimized for SpeechCraft TTS with accent support
    """
    
    @staticmethod
    def get_accent_instructions() -> str:
        """
        Get SpeechCraft accent and expression instructions
        """
        return """
Available SpeechCraft expressions and accents to use in the rewritten text:

EMOTIONAL EXPRESSIONS:
- [laughter] or [laughs] - for natural laughter
- [sighs] - for sighs and breathing sounds
- [gasps] - for surprise or shock
- [clears throat] - for throat clearing

SPEECH PATTERNS:
- Use "—" or "..." for natural hesitations and pauses
- CAPITALIZE words for EMPHASIS and important points
- Use [MAN] and [WOMAN] to bias toward male/female voices when needed

SPECIAL CONTENT:
- [music] - for background music or musical interludes
- ♪ text ♪ - for song lyrics or musical content

INSTRUCTIONS:
- Incorporate these naturally into the rewritten script
- Use [laughs] after humorous comments
- Add [sighs] for dramatic effect or when discussing serious topics
- Use CAPITALIZATION for key points and emphasis
- Include natural hesitations with "..." or "—"
- Add [clears throat] before important announcements
"""
    
    @staticmethod
    def create_rewrite_prompt() -> str:
        """
        Create the complete rewrite prompt for OpenAI
        """
        base_prompt = """You are an expert YouTube script rewriter. Your task is to:

1. UNDERSTAND the original script and its core message
2. CREATE a similar script suitable for another YouTube channel in the same niche
3. MAINTAIN the original meaning while making it unique and engaging
4. INCORPORATE natural speech patterns and expressions for TTS generation

REWRITING GUIDELINES:
- Keep the same core information and structure
- Make it sound natural and conversational
- Add personality and engagement
- Ensure it flows well for audio/speech
- Maintain appropriate length and pacing
"""
        
        accent_instructions = SpeechCraftPromptGenerator.get_accent_instructions()
        
        return f"""{base_prompt}

{accent_instructions}

Please rewrite the provided script following these guidelines and incorporating the SpeechCraft expressions naturally."""

# ---- Integration Example ----
class TTSProcessor:
    """
    Complete TTS processing pipeline combining OpenAI rewriting and SpeechCraft TTS
    """
    
    def __init__(self, transcript_processor, speechcraft_tts: SpeechCraftTTS):
        self.transcript_processor = transcript_processor
        self.tts = speechcraft_tts
        
        # Update the transcript processor's rewrite prompt
        self.transcript_processor.config.rewrite_prompt = SpeechCraftPromptGenerator.create_rewrite_prompt()
        
    def process_text_to_speech(
        self, 
        original_text: str, 
        voice: Optional[str] = None,
        output_path: Optional[str] = None,
        skip_rewrite: bool = False
    ) -> Tuple[str, np.ndarray, int]:
        """
        Complete pipeline: rewrite text with OpenAI and generate TTS
        
        Args:
            original_text: Original text to process
            voice: Voice to use for TTS
            output_path: Path to save audio file
            skip_rewrite: Skip OpenAI rewriting step
            
        Returns:
            Tuple of (rewritten_text, audio_numpy, sample_rate)
        """
        # Step 1: Rewrite text with OpenAI (if not skipped)
        if not skip_rewrite:
            logger.info("Rewriting text with OpenAI...")
            rewritten_text = self.transcript_processor.rewrite_transcript(original_text)
        else:
            rewritten_text = original_text
            
        logger.info("Rewritten text preview:")
        logger.info(rewritten_text[:200] + "..." if len(rewritten_text) > 200 else rewritten_text)
        
        # Step 2: Generate TTS
        logger.info("Generating TTS...")
        audio_numpy, sample_rate = self.tts.generate_tts(
            text=rewritten_text,
            voice=voice,
            output_path=output_path
        )
        
        return rewritten_text, audio_numpy, sample_rate

# ---- Usage Example ----
if __name__ == "__main__":
    # Import your existing config and transcript processor
    # from your_module import Config, TranscriptProcessor
    
    # Initialize components
    # config = Config()
    # transcript_processor = TranscriptProcessor(config)
    speechcraft_tts = SpeechCraftTTS(default_speaker="en_speaker_3")
    
    # Create TTS processor
    # tts_processor = TTSProcessor(transcript_processor, speechcraft_tts)
    
    # Example usage
    sample_text = """
    Today we're diving into the fascinating world of artificial intelligence. 
    It's absolutely revolutionizing everything we know about technology and human interaction.
    """
    
    # Generate TTS directly (using default speaker)
    audio_data, sr = speechcraft_tts.generate_tts(
        text="Hello everyone! [laughs] Welcome to our amazing show about AI... it's going to be INCREDIBLE! [clears throat]",
        output_path="output/sample_tts.wav",
        voice="en_speaker_3" # Explicitly use a speaker name to avoid voice cloning path
    )
    
    print("TTS generation completed!")
    print(f"Audio shape: {audio_data.shape}, Sample rate: {sr}")
