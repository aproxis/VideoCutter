"""
Standalone SpeechCraft TTS Module
Independent from OpenAI processor but can integrate when needed
"""

import os
import logging
from typing import Optional, Tuple, Dict, Any
import numpy as np
import torch.serialization # Import torch.serialization
from speechcraft import text2voice, voice2embedding
from media_toolkit import AudioFile

# Add numpy.core.multiarray.scalar to safe globals for torch.load
torch.serialization.add_safe_globals([np.core.multiarray.scalar])

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SpeechCraftTTS:
    """
    Standalone SpeechCraft TTS wrapper with voice cloning support
    """
    
    def __init__(self, default_speaker: str = "en_speaker_3"):
        """
        Initialize SpeechCraft TTS
        
        Args:
            default_speaker: Default speaker voice to use
        """
        self.default_speaker = default_speaker
        self.voice_embeddings = {}  # Cache for voice embeddings
        self.available_speakers = self._get_available_speakers()
        logger.info(f"SpeechCraftTTS initialized with default speaker: {default_speaker}")
    
    def _get_available_speakers(self) -> Dict[str, str]:
        """Get list of available speakers by language"""
        return {
            "english": ["en_speaker_0", "en_speaker_1", "en_speaker_2", "en_speaker_3", 
                       "en_speaker_4", "en_speaker_5", "en_speaker_6", "en_speaker_7", 
                       "en_speaker_8", "en_speaker_9"],
            "german": ["de_speaker_0", "de_speaker_1", "de_speaker_2"],
            "spanish": ["es_speaker_0", "es_speaker_1", "es_speaker_2"],
            "french": ["fr_speaker_0", "fr_speaker_1", "fr_speaker_2"],
            "hindi": ["hi_speaker_0", "hi_speaker_1", "hi_speaker_2"],
            "italian": ["it_speaker_0", "it_speaker_1", "it_speaker_2"],
            "japanese": ["ja_speaker_0", "ja_speaker_1", "ja_speaker_2"],
            "korean": ["ko_speaker_0", "ko_speaker_1", "ko_speaker_2"],
            "polish": ["pl_speaker_0", "pl_speaker_1", "pl_speaker_2"],
            "portuguese": ["pt_speaker_0", "pt_speaker_1", "pt_speaker_2"],
            "russian": ["ru_speaker_0", "ru_speaker_1", "ru_speaker_2"],
            "turkish": ["tr_speaker_0", "tr_speaker_1", "tr_speaker_2"],
            "chinese": ["zh_speaker_0", "zh_speaker_1", "zh_speaker_2"]
        }
    
    def list_speakers(self, language: Optional[str] = None) -> Dict[str, Any]:
        """
        List available speakers
        
        Args:
            language: Filter by language (optional)
            
        Returns:
            Dictionary of available speakers
        """
        if language:
            return {language: self.available_speakers.get(language, [])}
        return self.available_speakers
    
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
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
                
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
        output_path: Optional[str] = None,
        save_audio: bool = True
    ) -> Tuple[np.ndarray, int]:
        """
        Generate TTS audio from text
        
        Args:
            text: Text to convert to speech (with SpeechCraft accents)
            voice: Voice to use (speaker name or embedding name)
            output_path: Optional path to save audio file
            save_audio: Whether to save audio to file
            
        Returns:
            Tuple of (audio_numpy_array, sample_rate)
        """
        try:
            # Use provided voice or default speaker
            speaker_voice = voice or self.default_speaker
            
            logger.info(f"Generating TTS with voice: {speaker_voice}")
            logger.info(f"Text length: {len(text)} characters")
            logger.info(f"Text preview: {text[:100]}{'...' if len(text) > 100 else ''}")
            
            # Generate TTS
            if speaker_voice in self.voice_embeddings:
                # Use voice embedding
                logger.info("Using custom voice embedding")
                audio_numpy, sample_rate = text2voice(
                    text, 
                    voice=self.voice_embeddings[speaker_voice]
                )
            else:
                # Use speaker name
                logger.info("Using predefined speaker")
                audio_numpy, sample_rate = text2voice(
                    text, 
                    voice=speaker_voice
                )
            
            logger.info(f"TTS generated successfully. Sample rate: {sample_rate}, Audio shape: {audio_numpy.shape}")
            
            # Save audio if requested
            if save_audio and output_path:
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
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Convert and save using media-toolkit
            audio = AudioFile().from_np_array(audio_numpy, sr=sample_rate)
            audio.save(output_path)
            
            logger.info(f"Audio saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise

class SpeechCraftPrompts:
    """
    Standalone prompt generator for SpeechCraft TTS optimization
    """
    
    @staticmethod
    def get_accent_guide() -> str:
        """
        Get comprehensive SpeechCraft accent and expression guide
        """
        return """
═══════════════════════════════════════════════════════════════
                    SPEECHCRAFT ACCENT GUIDE
═══════════════════════════════════════════════════════════════

EMOTIONAL EXPRESSIONS:
• [laughter] or [laughs] - Natural laughter sounds
• [sighs] - Sighs and breathing sounds
• [gasps] - Surprise or shock reactions
• [clears throat] - Throat clearing before speaking

SPEECH PATTERNS:
• "—" or "..." - Natural hesitations and pauses
• CAPITALIZE - Words for EMPHASIS and important points
• [MAN] / [WOMAN] - Bias toward male/female voice characteristics

SPECIAL CONTENT:
• [music] - Background music or musical interludes
• ♪ lyrics ♪ - Song lyrics or musical content

USAGE EXAMPLES:
• "Welcome everyone! [laughs] Today we're discussing..."
• "This is REALLY important... [clears throat] let me explain."
• "The results were... [gasps] absolutely incredible!"
• "[sighs] Unfortunately, we need to address this issue."

═══════════════════════════════════════════════════════════════
"""
    
    @staticmethod
    def create_youtube_rewrite_prompt() -> str:
        """
        Create optimized prompt for YouTube script rewriting with SpeechCraft support
        """
        return """You are an expert YouTube script rewriter specializing in creating engaging, TTS-optimized content.

CORE OBJECTIVES:
1. UNDERSTAND the original script's message and purpose
2. CREATE a unique version suitable for another similar YouTube channel
3. MAINTAIN core information while adding fresh perspective
4. OPTIMIZE for natural speech synthesis and audience engagement

REWRITING GUIDELINES:
• Keep the same essential information and structure
• Make language conversational and natural
• Add personality and authentic engagement
• Ensure smooth flow for audio narration
• Maintain appropriate pacing and rhythm
• Include natural speech patterns and expressions

SPEECHCRAFT EXPRESSIONS TO INCORPORATE:
• [laughs] - After humorous or light-hearted comments
• [sighs] - For dramatic effect or serious topics
• [gasps] - For surprising revelations or statistics
• [clears throat] - Before important announcements
• CAPITALIZATION - For key points and emphasis
• "..." or "—" - For natural pauses and hesitations
• [music] - For transitions or background atmosphere

EXAMPLE TRANSFORMATIONS:
Original: "Artificial intelligence is changing technology."
Rewritten: "AI is COMPLETELY revolutionizing our world... [laughs] and honestly, it's both exciting and terrifying!"

Please rewrite the provided script naturally incorporating these elements."""

    @staticmethod
    def create_conversation_prompt() -> str:
        """
        Create prompt for conversational-style content
        """
        return """Transform this content into a natural, conversational format optimized for SpeechCraft TTS.

STYLE REQUIREMENTS:
• Sound like a friend explaining something interesting
• Use natural speech patterns with pauses and emphasis
• Include appropriate SpeechCraft expressions
• Make it engaging and easy to listen to
• Add personality without losing information

Please rewrite in a conversational, engaging style."""

class StandaloneTTSPipeline:
    """
    Complete standalone TTS pipeline
    Can work independently or integrate with external text processors
    """
    
    def __init__(self, default_speaker: str = "en_speaker_3", output_dir: str = "output"):
        """
        Initialize TTS pipeline
        
        Args:
            default_speaker: Default voice to use
            output_dir: Directory for output files
        """
        self.tts = SpeechCraftTTS(default_speaker)
        self.prompts = SpeechCraftPrompts()
        self.output_dir = output_dir
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Standalone TTS Pipeline initialized")
        logger.info(f"Default speaker: {default_speaker}")
        logger.info(f"Output directory: {output_dir}")
    
    def show_accent_guide(self):
        """Display the SpeechCraft accent guide"""
        print(self.prompts.get_accent_guide())
    
    def list_voices(self, language: Optional[str] = None):
        """List available voices"""
        speakers = self.tts.list_speakers(language)
        print("\n📢 AVAILABLE VOICES:")
        print("=" * 50)
        for lang, voices in speakers.items():
            print(f"\n{lang.upper()}:")
            for voice in voices:
                print(f"  • {voice}")
        print()
    
    def process_text_direct(
        self, 
        text: str,
        voice: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Tuple[np.ndarray, int, str]:
        """
        Process text directly to TTS (no rewriting)
        
        Args:
            text: Text to convert to speech
            voice: Voice to use
            filename: Output filename (auto-generated if None)
            
        Returns:
            Tuple of (audio_numpy, sample_rate, output_path)
        """
        if not filename:
            filename = f"tts_direct_{len(text)[:50]}_{voice or 'default'}.wav"
        
        output_path = os.path.join(self.output_dir, filename)
        
        logger.info("Processing text directly to TTS...")
        audio_numpy, sample_rate = self.tts.generate_tts(
            text=text,
            voice=voice,
            output_path=output_path
        )
        
        return audio_numpy, sample_rate, output_path
    
    def create_voice_clone(self, audio_file: str, voice_name: str) -> str:
        """
        Create voice clone from audio sample
        
        Args:
            audio_file: Path to audio sample
            voice_name: Name for the cloned voice
            
        Returns:
            Voice name identifier
        """
        return self.tts.create_voice_embedding(audio_file, voice_name)
    
    def get_youtube_prompt(self) -> str:
        """Get the YouTube rewrite prompt"""
        return self.prompts.create_youtube_rewrite_prompt()
    
    def process_with_external_rewriter(
        self,
        original_text: str,
        rewrite_function,
        voice: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Tuple[str, np.ndarray, int, str]:
        """
        Process text using external rewriter function (like your OpenAI processor)
        
        Args:
            original_text: Original text to process
            rewrite_function: Function that takes text and returns rewritten text
            voice: Voice to use for TTS
            filename: Output filename
            
        Returns:
            Tuple of (rewritten_text, audio_numpy, sample_rate, output_path)
        """
        logger.info("Using external rewriter...")
        
        # Use external rewrite function
        rewritten_text = rewrite_function(original_text)
        
        # Generate TTS
        if not filename:
            filename = f"tts_rewritten_{len(original_text)[:50]}.wav"
        
        output_path = os.path.join(self.output_dir, filename)
        
        audio_numpy, sample_rate = self.tts.generate_tts(
            text=rewritten_text,
            voice=voice,
            output_path=output_path
        )
        
        return rewritten_text, audio_numpy, sample_rate, output_path

# ---- Usage Examples ----
def main():
    """Example usage of the standalone TTS module"""
    
    # Initialize pipeline
    tts_pipeline = StandaloneTTSPipeline(
        default_speaker="en_speaker_3",
        output_dir="tts_output"
    )
    
    # Show available features
    print("🎤 STANDALONE SPEECHCRAFT TTS MODULE")
    print("=" * 60)
    
    # Show accent guide
    tts_pipeline.show_accent_guide()
    
    # List available voices
    tts_pipeline.list_voices("english")
    
    # Example 1: Direct TTS
    sample_text = """
    Welcome to our channel! [laughs] Today we're exploring the FASCINATING world of AI... 
    [clears throat] This is going to be an incredible journey! [gasps] 
    You won't believe what we've discovered!
    """
    
    print("🔊 Generating direct TTS...")
    audio_data, sr, path = tts_pipeline.process_text_direct(
        text=sample_text,
        voice="en_speaker_3",
        filename="example_direct.wav"
    )
    print(f"✅ Generated: {path}")
    print(f"   Audio shape: {audio_data.shape}, Sample rate: {sr}")
    
    # Example 2: Get prompt for external use
    print("\n📝 YouTube rewrite prompt:")
    prompt = tts_pipeline.get_youtube_prompt()
    print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    
    print("\n🎯 Module ready for integration or standalone use!")

if __name__ == "__main__":
    main()
