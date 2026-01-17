"""
Voice Engine - Handles voice recording and generation.
Supports both recording and TTS-based voice generation.
"""

import sounddevice as sd
import soundfile as sf
import pyttsx3
import os
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Basic voice engine for recording and TTS voice generation.
    For advanced emotional voice generation, use EmotionalVoiceEngine.
    """
    
    def __init__(self, audio_dir: Optional[str] = None):
        """
        Initialize voice engine.
        
        Args:
            audio_dir: Directory to store voice files
        """
        if audio_dir is None:
            audio_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets', 'audio'
            )
        
        self.audio_dir = audio_dir
        os.makedirs(self.audio_dir, exist_ok=True)
        logger.info(f"VoiceEngine initialized with audio dir: {audio_dir}")

    def record_voice(self, duration: float = 5, filename: Optional[str] = None,
                    samplerate: int = 44100) -> str:
        """
        Record voice from microphone.
        
        Args:
            duration: Duration to record in seconds
            filename: Output filename
            samplerate: Sample rate for recording
            
        Returns:
            Path to recorded audio file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{timestamp}.wav"
        
        filepath = os.path.join(self.audio_dir, filename)
        
        try:
            logger.info(f"Recording voice for {duration} seconds...")
            recording = sd.rec(int(duration * samplerate), samplerate=samplerate,
                             channels=1, dtype='float64')
            sd.wait()
            
            sf.write(filepath, recording, samplerate)
            logger.info(f"Voice recorded: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error recording voice: {e}")
            raise

    def generate_ai_voice(self, text: str, filename: Optional[str] = None,
                         rate: int = 150, volume: float = 1.0) -> str:
        """
        Generate voice using TTS.
        
        Args:
            text: Text to convert to speech
            filename: Output filename
            rate: Speech rate (default 150)
            volume: Volume level (0.0-1.0)
            
        Returns:
            Path to generated audio file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_voice_{timestamp}.wav"
        
        filepath = os.path.join(self.audio_dir, filename)
        
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            
            engine.save_to_file(text, filepath)
            engine.runAndWait()
            
            logger.info(f"AI voice generated: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating AI voice: {e}")
            raise