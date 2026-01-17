"""
Audio-Visual Merger Module - Core integration for audio, visual effects, and rendering.
Combines lip-sync, emotional voice, background music, SFX, and VFX into final output.
"""

import os
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import logging
import json
from datetime import datetime

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
except ImportError:
    logging.warning("MoviePy not installed. Install with: pip install moviepy")

try:
    import librosa
    from scipy import signal
except ImportError:
    logging.warning("Librosa/SciPy not installed. Install with: pip install librosa scipy")

try:
    from pydub import AudioSegment
except ImportError:
    logging.warning("Pydub not installed. Install with: pip install pydub")

logger = logging.getLogger(__name__)


@dataclass
class AudioTrack:
    """Represents an audio track with metadata."""
    path: str
    name: str
    duration: float
    volume: float = 1.0
    start_time: float = 0.0
    fade_in: float = 0.0
    fade_out: float = 0.0


@dataclass
class VisualEffect:
    """Represents a visual effect to apply."""
    effect_type: str  # 'color_grade', 'grain', 'blur', 'sharpen', 'vignette'
    intensity: float
    start_frame: int
    end_frame: int
    parameters: Dict = None


class AudioVisualMerger:
    """
    Merges audio, visual effects, and video content into a complete movie.
    Handles lip-sync, audio ducking, VFX, and multi-layer audio mixing.
    """

    def __init__(self, output_dir: Optional[str] = None, temp_dir: Optional[str] = None):
        """
        Initialize the Audio-Visual Merger.
        
        Args:
            output_dir: Directory for final output files
            temp_dir: Directory for temporary processing files
        """
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'output'
            )
        if temp_dir is None:
            temp_dir = os.path.join(output_dir, 'temp')
        
        self.output_dir = output_dir
        self.temp_dir = temp_dir
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.audio_tracks: List[AudioTrack] = []
        self.visual_effects: List[VisualEffect] = []
        self.processing_log = []
        
        logger.info(f"AudioVisualMerger initialized. Output: {output_dir}")

    # ==================== Audio Processing ====================

    def add_audio_track(self, audio_path: str, name: str, volume: float = 1.0,
                       start_time: float = 0.0, fade_in: float = 0.0,
                       fade_out: float = 0.0) -> AudioTrack:
        """
        Add an audio track to the project.
        
        Args:
            audio_path: Path to audio file
            name: Track name (for identification)
            volume: Volume level (0.0 - 1.0)
            start_time: When to start this track (seconds)
            fade_in: Fade-in duration (seconds)
            fade_out: Fade-out duration (seconds)
            
        Returns:
            AudioTrack object
        """
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Get audio duration
        try:
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0  # Convert to seconds
        except Exception as e:
            logger.warning(f"Could not determine duration: {e}")
            duration = 0.0
        
        track = AudioTrack(
            path=audio_path,
            name=name,
            duration=duration,
            volume=volume,
            start_time=start_time,
            fade_in=fade_in,
            fade_out=fade_out
        )
        
        self.audio_tracks.append(track)
        self.processing_log.append(f"Added audio track: {name} ({duration:.2f}s)")
        logger.info(f"Added audio track: {name}")
        
        return track

    def apply_audio_ducking(self, voice_track_path: str, music_track_path: str,
                           output_path: str, duck_amount_db: float = -12,
                           attack_ms: float = 100, release_ms: float = 200) -> str:
        """
        Apply audio ducking effect - reduces music volume when voice is present.
        
        Args:
            voice_track_path: Path to voice/dialogue audio
            music_track_path: Path to music/background audio
            output_path: Path to save ducked music
            duck_amount_db: How much to reduce volume (in dB)
            attack_ms: Attack time for volume reduction
            release_ms: Release time for volume restoration
            
        Returns:
            Path to ducked audio file
        """
        logger.info(f"Applying audio ducking: {music_track_path}")
        
        try:
            # Load audio files
            voice, sr_voice = librosa.load(voice_track_path, sr=None)
            music, sr_music = librosa.load(music_track_path, sr=None)
            
            # Ensure same sample rate
            if sr_voice != sr_music:
                voice = librosa.resample(voice, orig_sr=sr_voice, target_sr=sr_music)
                sr = sr_music
            else:
                sr = sr_voice
            
            # Pad arrays to same length
            max_len = max(len(voice), len(music))
            voice = np.pad(voice, (0, max_len - len(voice)), mode='constant')
            music = np.pad(music, (0, max_len - len(music)), mode='constant')
            
            # Calculate voice activity (RMS energy)
            voice_rms = np.sqrt(np.convolve(voice**2, np.ones(2048)/2048, mode='same'))
            
            # Normalize voice activity to 0-1
            voice_activity = voice_rms / (np.max(voice_rms) + 1e-10)
            
            # Create ducking envelope
            attack_samples = int(attack_ms * sr / 1000)
            release_samples = int(release_ms * sr / 1000)
            
            duck_envelope = np.ones_like(voice_activity)
            voice_threshold = 0.1
            
            for i in range(len(duck_envelope)):
                if voice_activity[i] > voice_threshold:
                    # During voice: apply ducking
                    duck_envelope[i] = 10 ** (duck_amount_db / 20.0)
                else:
                    # Smooth transition
                    if i > 0:
                        if duck_envelope[i-1] < 1.0:
                            # Slowly release
                            duck_envelope[i] = min(1.0, duck_envelope[i-1] + 1.0/release_samples)
            
            # Apply ducking envelope to music
            ducked_music = music * duck_envelope
            
            # Normalize to prevent clipping
            ducked_music = np.clip(ducked_music, -1.0, 1.0)
            
            # Save output
            import soundfile as sf
            sf.write(output_path, ducked_music, sr)
            
            self.processing_log.append(f"Applied ducking: {output_path}")
            logger.info(f"Audio ducking applied: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error applying audio ducking: {e}")
            raise

    def mix_audio_tracks(self, output_path: str, normalize: bool = True) -> str:
        """
        Mix all added audio tracks into a single audio file.
        
        Args:
            output_path: Path to save mixed audio
            normalize: Whether to normalize output
            
        Returns:
            Path to mixed audio file
        """
        if not self.audio_tracks:
            logger.warning("No audio tracks to mix")
            return None
        
        logger.info(f"Mixing {len(self.audio_tracks)} audio tracks")
        
        try:
            # Load all audio tracks
            combined = None
            sr = None
            
            for track in self.audio_tracks:
                audio = AudioSegment.from_file(track.path)
                
                # Apply volume
                audio = audio + (20 * np.log10(track.volume)) if track.volume != 1.0 else audio
                
                # Apply fade in/out
                if track.fade_in > 0:
                    audio = audio.fade_in(int(track.fade_in * 1000))
                if track.fade_out > 0:
                    audio = audio.fade_out(int(track.fade_out * 1000))
                
                # Overlay on combined
                if combined is None:
                    combined = audio
                else:
                    combined = combined.overlay(audio, position=int(track.start_time * 1000))
            
            # Normalize if requested
            if normalize:
                combined = combined.normalize()
            
            # Export
            combined.export(output_path, format='wav')
            
            self.processing_log.append(f"Mixed {len(self.audio_tracks)} tracks: {output_path}")
            logger.info(f"Audio tracks mixed: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error mixing audio tracks: {e}")
            raise

    # ==================== Visual Effects Processing ====================

    def add_visual_effect(self, effect_type: str, intensity: float,
                         start_frame: int, end_frame: int,
                         parameters: Optional[Dict] = None) -> VisualEffect:
        """
        Add a visual effect to be applied to video.
        
        Args:
            effect_type: Type of effect ('color_grade', 'grain', 'blur', 'sharpen', 'vignette')
            intensity: Effect intensity (0.0 - 1.0)
            start_frame: Frame to start effect
            end_frame: Frame to end effect
            parameters: Additional effect parameters
            
        Returns:
            VisualEffect object
        """
        effect = VisualEffect(
            effect_type=effect_type,
            intensity=intensity,
            start_frame=start_frame,
            end_frame=end_frame,
            parameters=parameters or {}
        )
        
        self.visual_effects.append(effect)
        self.processing_log.append(f"Added effect: {effect_type} (frames {start_frame}-{end_frame})")
        logger.info(f"Added visual effect: {effect_type}")
        
        return effect

    def apply_color_grading(self, frame: np.ndarray, intensity: float,
                           color_temp: str = 'warm') -> np.ndarray:
        """
        Apply color grading to a frame.
        
        Args:
            frame: Input frame (BGR)
            intensity: Effect intensity (0.0 - 1.0)
            color_temp: 'warm', 'cool', 'cinematic', 'vintage'
            
        Returns:
            Color-graded frame
        """
        frame_float = frame.astype(np.float32) / 255.0
        
        if color_temp == 'warm':
            # Boost red and yellow channels
            frame_float[:, :, 2] = np.clip(frame_float[:, :, 2] * (1 + intensity * 0.3), 0, 1)
            frame_float[:, :, 1] = np.clip(frame_float[:, :, 1] * (1 + intensity * 0.1), 0, 1)
        
        elif color_temp == 'cool':
            # Boost blue channel
            frame_float[:, :, 0] = np.clip(frame_float[:, :, 0] * (1 + intensity * 0.3), 0, 1)
        
        elif color_temp == 'cinematic':
            # Reduce saturation and boost contrast
            frame_float = cv2.cvtColor(frame_float, cv2.COLOR_BGR2HSV)
            frame_float[:, :, 1] *= (1 - intensity * 0.3)
            frame_float = cv2.cvtColor(frame_float, cv2.COLOR_HSV2BGR)
        
        elif color_temp == 'vintage':
            # Reduce contrast and add slight color cast
            frame_float = frame_float * (1 - intensity * 0.2) + intensity * 0.2 * 0.5
        
        return np.clip(frame_float * 255, 0, 255).astype(np.uint8)

    def apply_cinematic_grain(self, frame: np.ndarray, intensity: float,
                             grain_size: int = 2) -> np.ndarray:
        """
        Apply cinematic grain effect.
        
        Args:
            frame: Input frame
            intensity: Effect intensity
            grain_size: Size of grain particles
            
        Returns:
            Frame with grain effect
        """
        h, w = frame.shape[:2]
        
        # Generate grain pattern
        grain = np.random.normal(0, intensity * 20, (h, w))
        grain = cv2.GaussianBlur(grain, (grain_size, grain_size), 0)
        
        # Apply grain to each channel
        frame_float = frame.astype(np.float32)
        for i in range(3):
            frame_float[:, :, i] += grain
        
        return np.clip(frame_float, 0, 255).astype(np.uint8)

    def apply_vignette(self, frame: np.ndarray, intensity: float) -> np.ndarray:
        """
        Apply vignette effect (darker edges).
        
        Args:
            frame: Input frame
            intensity: Effect intensity
            
        Returns:
            Frame with vignette
        """
        h, w = frame.shape[:2]
        
        # Create vignette mask
        kernel_x = cv2.getGaussianKernel(w, w/2)
        kernel_y = cv2.getGaussianKernel(h, h/2)
        kernel = kernel_y * kernel_x.T
        
        mask = kernel / kernel.max()
        mask = np.power(mask, intensity)
        
        # Apply mask to each channel
        frame_float = frame.astype(np.float32)
        for i in range(3):
            frame_float[:, :, i] *= mask
        
        return np.clip(frame_float, 0, 255).astype(np.uint8)

    def process_video_with_effects(self, input_video: str, output_video: str) -> str:
        """
        Process video and apply all visual effects.
        
        Args:
            input_video: Path to input video
            output_video: Path to save output video
            
        Returns:
            Path to processed video
        """
        logger.info(f"Processing video with effects: {input_video}")
        
        cap = cv2.VideoCapture(input_video)
        if not cap.isOpened():
            logger.error(f"Cannot open video: {input_video}")
            raise ValueError(f"Cannot open video: {input_video}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply effects for this frame
                for effect in self.visual_effects:
                    if effect.start_frame <= frame_count <= effect.end_frame:
                        if effect.effect_type == 'color_grade':
                            color_temp = effect.parameters.get('color_temp', 'warm')
                            frame = self.apply_color_grading(frame, effect.intensity, color_temp)
                        
                        elif effect.effect_type == 'grain':
                            frame = self.apply_cinematic_grain(frame, effect.intensity)
                        
                        elif effect.effect_type == 'vignette':
                            frame = self.apply_vignette(frame, effect.intensity)
                        
                        elif effect.effect_type == 'blur':
                            kernel_size = int(effect.intensity * 21) * 2 + 1
                            frame = cv2.blur(frame, (kernel_size, kernel_size))
                        
                        elif effect.effect_type == 'sharpen':
                            kernel = np.array([[-1, -1, -1],
                                             [-1,  9, -1],
                                             [-1, -1, -1]]) * effect.intensity / 8
                            frame = cv2.filter2D(frame, -1, kernel)
                
                out.write(frame)
                frame_count += 1
                
                if frame_count % 30 == 0:
                    logger.info(f"Processed {frame_count}/{total_frames} frames")
            
            cap.release()
            out.release()
            
            self.processing_log.append(f"Processed video with {len(self.visual_effects)} effects: {output_video}")
            logger.info(f"Video processing complete: {output_video}")
            return output_video
            
        except Exception as e:
            cap.release()
            logger.error(f"Error processing video: {e}")
            raise

    # ==================== Complete Merge ====================

    def merge_video_and_audio(self, video_path: str, audio_path: str,
                             output_path: str, video_duration: Optional[float] = None) -> str:
        """
        Merge video and audio into final output.
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path to save final output
            video_duration: Optional duration to trim video to (seconds)
            
        Returns:
            Path to merged output
        """
        logger.info(f"Merging video and audio: {output_path}")
        
        try:
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Trim to duration if specified
            if video_duration:
                video = video.subclipped(0, min(video.duration, video_duration))
                audio = audio.subclipped(0, min(audio.duration, video_duration))
            
            # Ensure audio matches video duration
            if audio.duration < video.duration:
                logger.warning(f"Audio ({audio.duration}s) shorter than video ({video.duration}s)")
            
            # Composite
            final = video.set_audio(audio)
            
            # Write output
            final.write_videofile(output_path, verbose=False, logger=None)
            
            self.processing_log.append(f"Merged video and audio: {output_path}")
            logger.info(f"Merge complete: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error merging video and audio: {e}")
            raise

    def get_processing_log(self) -> List[str]:
        """Get processing log."""
        return self.processing_log

    def export_processing_report(self, report_path: Optional[str] = None) -> str:
        """
        Export processing report as JSON.
        
        Args:
            report_path: Path to save report
            
        Returns:
            Path to report file
        """
        if report_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(self.output_dir, f"processing_report_{timestamp}.json")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'audio_tracks': [
                {
                    'name': t.name,
                    'duration': t.duration,
                    'volume': t.volume,
                    'start_time': t.start_time
                }
                for t in self.audio_tracks
            ],
            'visual_effects': [
                {
                    'type': e.effect_type,
                    'intensity': e.intensity,
                    'frames': f"{e.start_frame}-{e.end_frame}"
                }
                for e in self.visual_effects
            ],
            'processing_log': self.processing_log
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Processing report exported: {report_path}")
        return report_path
