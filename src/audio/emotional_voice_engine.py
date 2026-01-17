"""
Enhanced Voice Engine with emotional tone support and TTS improvements.
Extends basic voice generation with emotional expression and quality enhancements.
"""

import os
import numpy as np
import pyttsx3
from pydub import AudioSegment
from pydub.effects import normalize
import librosa
import soundfile as sf
from typing import Optional, Tuple, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class EmotionalVoiceEngine:
    """
    Enhanced voice generation with emotional tones and audio quality improvements.
    """
    
    # Emotion presets with pitch, rate, and volume adjustments
    EMOTION_PRESETS = {
        'neutral': {'pitch': 1.0, 'rate': 150, 'volume': 1.0},
        'happy': {'pitch': 1.2, 'rate': 170, 'volume': 1.1},
        'sad': {'pitch': 0.8, 'rate': 120, 'volume': 0.9},
        'angry': {'pitch': 0.95, 'rate': 180, 'volume': 1.15},
        'excited': {'pitch': 1.3, 'rate': 200, 'volume': 1.2},
        'concerned': {'pitch': 0.9, 'rate': 140, 'volume': 0.95},
        'whisper': {'pitch': 0.7, 'rate': 100, 'volume': 0.5},
    }

    def __init__(self, audio_dir: Optional[str] = None):
        """
        Initialize the emotional voice engine.
        
        Args:
            audio_dir: Directory to store audio files
        """
        if audio_dir is None:
            audio_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets', 'audio'
            )
        
        self.audio_dir = audio_dir
        os.makedirs(self.audio_dir, exist_ok=True)
        
        # Initialize pyttsx3 engines for different voices
        self.engines = {}
        self._init_engines()
        
        logger.info(f"EmotionalVoiceEngine initialized with audio dir: {audio_dir}")

    def _init_engines(self):
        """Initialize multiple TTS engines for different voices."""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Create engines for available voices
            for i, voice in enumerate(voices[:3]):  # Limit to 3 voices
                self.engines[f'voice_{i}'] = {
                    'engine': pyttsx3.init(),
                    'voice_id': voice.id,
                    'name': voice.name
                }
            
            logger.info(f"Initialized {len(self.engines)} voice variants")
        except Exception as e:
            logger.warning(f"Error initializing voices: {e}. Using default.")
            self.engines['default'] = {'engine': pyttsx3.init()}

    def generate_emotional_voice(self, text: str, emotion: str = 'neutral',
                                voice_variant: str = 'voice_0',
                                filename: Optional[str] = None) -> str:
        """
        Generate voice with emotional tone.
        
        Args:
            text: Text to convert to speech
            emotion: Emotion type (see EMOTION_PRESETS keys)
            voice_variant: Which voice to use
            filename: Output filename
            
        Returns:
            Path to generated audio file
        """
        if emotion not in self.EMOTION_PRESETS:
            logger.warning(f"Unknown emotion '{emotion}', using 'neutral'")
            emotion = 'neutral'
        
        emotion_config = self.EMOTION_PRESETS[emotion]
        
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_{emotion}_{timestamp}.wav"
        
        filepath = os.path.join(self.audio_dir, filename)
        
        try:
            # Get engine
            if voice_variant in self.engines:
                engine = self.engines[voice_variant]['engine']
                if 'voice_id' in self.engines[voice_variant]:
                    engine.setProperty('voice', self.engines[voice_variant]['voice_id'])
            else:
                engine = pyttsx3.init()
            
            # Apply emotion settings
            engine.setProperty('rate', emotion_config['rate'])
            
            # Generate initial audio
            engine.save_to_file(text, filepath)
            engine.runAndWait()
            
            # Post-process audio for pitch and volume adjustments
            self._apply_emotional_processing(filepath, emotion_config)
            
            logger.info(f"Generated emotional voice: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating emotional voice: {e}")
            raise

    def _apply_emotional_processing(self, filepath: str, emotion_config: dict):
        """
        Apply pitch and volume adjustments to audio file.
        
        Args:
            filepath: Path to audio file
            emotion_config: Emotion configuration with pitch and volume
        """
        try:
            # Load audio
            y, sr = librosa.load(filepath, sr=None)
            
            # Apply pitch shift
            pitch_factor = emotion_config['pitch']
            if pitch_factor != 1.0:
                # Pitch shift in semitones (1.2x pitch ≈ 3.86 semitones)
                semitones = 12 * np.log2(pitch_factor)
                y = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)
            
            # Apply volume adjustment
            volume_factor = emotion_config['volume']
            y = y * volume_factor
            
            # Normalize and prevent clipping
            y = np.clip(y, -1.0, 1.0)
            
            # Save processed audio
            sf.write(filepath, y, sr)
            
        except Exception as e:
            logger.warning(f"Could not apply emotional processing: {e}")

    def blend_emotions(self, text: str, emotions: List[Tuple[str, float]],
                      filename: Optional[str] = None) -> str:
        """
        Generate voice with blended emotions.
        
        Args:
            text: Text to convert to speech
            emotions: List of (emotion, weight) tuples
            filename: Output filename
            
        Returns:
            Path to generated audio file
        """
        if not emotions:
            emotions = [('neutral', 1.0)]
        
        # Normalize weights
        total_weight = sum(w for _, w in emotions)
        emotions = [(e, w/total_weight) for e, w in emotions]
        
        # Generate audio for each emotion
        audio_segments = []
        for emotion, weight in emotions:
            temp_path = self.generate_emotional_voice(text, emotion)
            audio = AudioSegment.from_wav(temp_path)
            
            # Adjust volume based on weight
            audio = audio + (20 * np.log10(weight))  # Convert weight to dB
            audio_segments.append(audio)
        
        # Mix audio segments
        blended = audio_segments[0]
        for segment in audio_segments[1:]:
            blended = blended.overlay(segment)
        
        if filename is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"voice_blended_{timestamp}.wav"
        
        filepath = os.path.join(self.audio_dir, filename)
        blended.export(filepath, format='wav')
        
        logger.info(f"Generated blended emotion voice: {filepath}")
        return filepath

    def add_audio_effects(self, filepath: str, effects: List[str],
                         output_path: Optional[str] = None) -> str:
        """
        Add audio effects to voice (reverb, echo, compression).
        
        Args:
            filepath: Input audio file path
            effects: List of effects to apply
            output_path: Output file path
            
        Returns:
            Path to processed audio file
        """
        if output_path is None:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                self.audio_dir,
                f"voice_effects_{timestamp}.wav"
            )
        
        try:
            audio = AudioSegment.from_wav(filepath)
            
            if 'normalize' in effects:
                audio = normalize(audio)
            
            if 'compress' in effects:
                # Apply dynamic range compression
                audio = self._apply_compression(audio)
            
            audio.export(output_path, format='wav')
            logger.info(f"Applied effects and saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error applying audio effects: {e}")
            return filepath

    def _apply_compression(self, audio: AudioSegment, threshold_db: float = -20,
                          ratio: float = 4.0) -> AudioSegment:
        """
        Apply dynamic range compression to audio.
        
        Args:
            audio: Input audio segment
            threshold_db: Threshold in dB
            ratio: Compression ratio
            
        Returns:
            Compressed audio segment
        """
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
        samples = samples / np.iinfo(np.int16).max
        
        # Calculate RMS
        rms = np.sqrt(np.mean(samples**2))
        db = 20 * np.log10(rms + 1e-10)
        
        # Apply compression
        if db > threshold_db:
            excess = db - threshold_db
            reduction = excess * (1 - 1/ratio)
            gain_linear = 10 ** (-reduction / 20)
            samples = samples * gain_linear
        
        # Convert back
        samples = np.clip(samples, -1, 1) * np.iinfo(np.int16).max
        
        return audio._spawn(samples.astype(np.int16).tobytes())

    def get_available_emotions(self) -> List[str]:
        """Get list of available emotions."""
        return list(self.EMOTION_PRESETS.keys())

    def get_available_voices(self) -> List[str]:
        """Get list of available voice variants."""
        return list(self.engines.keys())

    def validate_emotion(self, emotion: str) -> bool:
        """Check if emotion is valid."""
        return emotion in self.EMOTION_PRESETS
