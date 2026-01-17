# Srijan Engine - Advanced Audio-Visual Features Documentation

## Overview

Srijan Engine has been upgraded with advanced audio-visual processing capabilities designed for professional text-to-movie generation, with specific support for the Saipooja Warehouse project.

## New Features

### 1. Advanced Audio & Lip-Sync

#### Lip-Sync Engine (`audio/lip_sync_engine.py`)
- **MediaPipe Integration**: Real-time facial landmark detection
- **Mouth Analysis**: Calculates mouth openness and shape (viseme detection)
- **Mouth Region Extraction**: Isolates mouth area from video frames
- **Wav2Lip Support**: Framework for AI-based lip-sync synthesis
- **Video Analysis**: Processes entire videos to extract lip-sync data

**Key Classes:**
- `LipSyncEngine`: Main lip-sync processing engine

**Example Usage:**
```python
from audio.lip_sync_engine import LipSyncEngine

engine = LipSyncEngine()

# Process video for lip-sync
frame_data = engine.process_video_for_lipsync(
    video_path="input_video.mp4",
    output_debug_path="debug_lipsync.mp4"
)

# Extract mouth region
landmarks = engine.detect_face_landmarks(frame)
mouth = engine.extract_mouth_region(frame, landmarks)
```

#### Emotional Voice Engine (`audio/emotional_voice_engine.py`)
- **Emotion Presets**: 7 emotional tone presets (neutral, happy, sad, angry, excited, concerned, whisper)
- **Voice Variants**: Support for multiple voice options
- **Emotion Blending**: Mix multiple emotions for nuanced delivery
- **Audio Effects**: Compression, normalization, and effects processing

**Key Classes:**
- `EmotionalVoiceEngine`: Advanced TTS with emotional tones

**Emotion Presets:**
- `neutral`: Standard speech
- `happy`: Higher pitch, faster rate
- `sad`: Lower pitch, slower rate
- `angry`: Aggressive delivery
- `excited`: High energy
- `concerned`: Worried tone
- `whisper`: Soft, quiet

**Example Usage:**
```python
from audio.emotional_voice_engine import EmotionalVoiceEngine

engine = EmotionalVoiceEngine()

# Generate emotional voice
audio_path = engine.generate_emotional_voice(
    text="Welcome to the warehouse!",
    emotion="happy",
    filename="welcome.wav"
)

# Blend emotions for complex delivery
blended = engine.blend_emotions(
    text="We have some concerns about the inventory.",
    emotions=[("concerned", 0.7), ("neutral", 0.3)]
)

# Add effects
enhanced = engine.add_audio_effects(
    filepath=audio_path,
    effects=['normalize', 'compress']
)
```

### 2. Background Music & Sound Effects with Audio Ducking

#### Audio-Visual Merger (`audio/audio_visual_merger.py`)

**Audio Ducking**: Automatically reduces background music volume when dialogue is present.

**Key Features:**
- Multi-track audio mixing
- Automatic volume ducking
- Fade in/out support
- Audio normalization
- Processing logging

**Example Usage:**
```python
from audio.audio_visual_merger import AudioVisualMerger

merger = AudioVisualMerger()

# Add audio tracks
merger.add_audio_track(
    audio_path="dialogue.wav",
    name="Dialogue",
    volume=1.0
)

merger.add_audio_track(
    audio_path="background_music.wav",
    name="Background Music",
    volume=0.8,
    fade_in=0.5,
    fade_out=0.5
)

# Apply audio ducking
ducked_music = merger.apply_audio_ducking(
    voice_track_path="dialogue.wav",
    music_track_path="background_music.wav",
    output_path="ducked_music.wav",
    duck_amount_db=-12,
    attack_ms=100,
    release_ms=200
)

# Mix all tracks
mixed_audio = merger.mix_audio_tracks("final_audio.wav")

# Merge with video
final_video = merger.merge_video_and_audio(
    video_path="rendered_video.mp4",
    audio_path="final_audio.wav",
    output_path="final_output.mp4"
)
```

### 3. VFX & Rendering

#### VFX Processor (`blender/vfx_processor.py`)

**Color Grading Styles:**
- `teal_orange`: Cinematic teal shadows, orange highlights
- `blue_yellow`: Cool/warm color contrast
- `desaturated`: Dramatic desaturation
- `warm`: Vintage warm look

**Visual Effects:**
- Professional LUT-based color grading
- Film grain (with optional color)
- Lens distortion (barrel/pincushion)
- Motion blur (horizontal, vertical, diagonal)
- Chromatic aberration
- Unsharp mask for detail enhancement
- Edge enhancement

**Example Usage:**
```python
from blender.vfx_processor import VFXProcessor, BlenderParticleEffects

# VFX Processing
vfx = VFXProcessor()

vfx_config = {
    'color_grade': 'teal_orange',
    'grain': 0.05,
    'sharpness': 1.0,
    'distortion': 0.02
}

processed_video = vfx.process_video_with_vfx(
    input_path="raw_video.mp4",
    output_path="vfx_processed.mp4",
    vfx_config=vfx_config
)

# Blender Particle Effects
blender_fx = BlenderParticleEffects()

# Generate Blender scripts for particle effects
blender_fx.generate_dust_particles_script(
    output_script="dust_effects.py",
    intensity=0.8,
    particle_count=5000
)

blender_fx.generate_smoke_effects_script(
    output_script="smoke_effects.py",
    intensity=0.6
)

blender_fx.generate_vehicle_effects_script(
    output_script="truck_exhaust.py",
    vehicle_type="truck",
    intensity=0.7
)
```

### 4. Warehouse Assets & Inventory Management

#### Warehouse Assets Manager (`blender/warehouse_assets_manager.py`)

**Supported Asset Types:**
- `FORKLIFT`: Industrial forklifts
- `MEDICINE_BOX`: Pharmaceutical packaging
- `CONTAINER_TRUCK`: Large transport trucks
- `SHELF`: Industrial shelving
- `PALLET`: Storage pallets
- `WAREHOUSE_STRUCTURE`: Building elements
- `LIGHTING`: Light objects
- `CAMERA`: Camera setups
- `PARTICLE_SYSTEM`: VFX particles

**Key Features:**
- Asset registry and inventory
- Scene management
- Asset positioning and scaling
- Automated Blender script generation
- Scene configuration export

**Example Usage:**
```python
from blender.warehouse_assets_manager import WarehouseAssetsManager, AssetType

manager = WarehouseAssetsManager()

# Get available assets
forklift = manager.get_asset("forklift_001")
trucks = manager.get_assets_by_type(AssetType.CONTAINER_TRUCK)

# Create a scene
scene = manager.create_scene(
    scene_name="Loading Dock",
    scene_id="loading_dock_001",
    description="Warehouse loading area with trucks and forklifts"
)

# Add assets to scene with positioning
manager.add_asset_to_scene(
    scene_id="loading_dock_001",
    asset_id="container_truck_001",
    position=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1.0, 1.0, 1.0)
)

manager.add_asset_to_scene(
    scene_id="loading_dock_001",
    asset_id="forklift_001",
    position=(5, 0, 0),
    scale=(1.0, 1.0, 1.0)
)

# Export configuration
manager.export_scene_config(
    scene_id="loading_dock_001",
    output_path="scene_config.json"
)

# Generate Blender setup script
manager.generate_blender_setup_script(
    scene_id="loading_dock_001",
    output_script="setup_scene.py"
)

# Get statistics
stats = manager.get_asset_statistics()
print(f"Total assets: {stats['total_assets']}")
print(f"By type: {stats['by_type']}")
```

## Integrated Workflow Example

See `src/integration_example.py` for comprehensive examples combining all modules.

**To run the integration example:**
```bash
cd src
python integration_example.py
```

## Dependencies

### New Required Packages (Added to requirements.txt)

```
# Audio Processing & Lip-Sync
pydub>=0.25.1
wav2lip>=0.0.1
moviepy>=1.0.3

# VFX & Visual Effects
imageio>=2.9.0
imageio-ffmpeg>=0.4.8
scikit-image>=0.20.0

# ML & Computer Vision
torch>=2.0.0
torchvision>=0.15.0
tensorflow>=2.12.0
transformers>=4.30.0

# Additional utilities
resampy>=0.4.2
soundata>=0.1.0
numba>=0.57.0
```

### Updated Existing Packages

```
customtkinter>=5.0
google-genai
python-dotenv
sounddevice>=0.4.6
soundfile>=0.12.0
gtts>=2.3.0
pyttsx3>=2.90
librosa>=0.10.0
numpy>=1.23.0
scipy>=1.9.0
Pillow>=10.0.0
opencv-python>=4.8.0
mediapipe>=0.10.0
psutil>=5.9.0
```

## Installation

```bash
# Install updated requirements
pip install -r requirements.txt

# Or install specific new packages
pip install pydub moviepy librosa scipy opencv-python mediapipe torch torchvision
```

## Module Structure

```
src/
├── audio/
│   ├── __init__.py
│   ├── voice_engine.py          # Basic voice recording/generation
│   ├── emotional_voice_engine.py # Enhanced emotional TTS
│   ├── lip_sync_engine.py        # Lip-sync with MediaPipe
│   └── audio_visual_merger.py    # Audio mixing, effects, and merging
│
├── blender/
│   ├── __init__.py
│   ├── vfx_processor.py          # Visual effects processing
│   ├── warehouse_assets_manager.py # Asset inventory & scenes
│   └── renderer.py               # Blender rendering
│
└── integration_example.py        # Complete usage examples
```

## Audio Ducking Algorithm

The audio ducking implementation:

1. **Analysis Phase**: Calculates voice activity using RMS energy
2. **Threshold Detection**: Detects voice presence above threshold
3. **Ducking Envelope**: Creates smooth envelope for volume reduction
4. **Attack/Release**: Configurable attack and release times for smooth transitions
5. **Application**: Applies envelope to background music track
6. **Normalization**: Prevents clipping on final output

**Parameters:**
- `duck_amount_db`: How much to reduce (-12 dB = 1/4 volume)
- `attack_ms`: Time to reach full ducking (default: 100ms)
- `release_ms`: Time to restore volume (default: 200ms)

## Color Grading Styles

### Teal & Orange
Professional cinematic look with teal shadows and orange highlights.
```python
frame = vfx.apply_cinematic_color_grade(frame, 'teal_orange')
```

### Blue & Yellow
Cool shadows, warm highlights for visual contrast.
```python
frame = vfx.apply_cinematic_color_grade(frame, 'blue_yellow')
```

### Desaturated
Reduced saturation for dramatic effect.
```python
frame = vfx.apply_cinematic_color_grade(frame, 'desaturated')
```

### Warm/Vintage
Warm color cast for vintage look.
```python
frame = vfx.apply_cinematic_color_grade(frame, 'warm')
```

## Blender Particle Effects

The system can generate Blender Python scripts for:

1. **Dust Particles**: Ambient dust effects in warehouses
2. **Smoke/Exhaust**: Vehicle exhaust or atmospheric effects
3. **Fire Effects**: For emergency scenarios
4. **Vehicle-Specific Effects**: Customized for trucks, forklifts, etc.

These scripts can be run in Blender to add particles directly to your scene.

## Performance Considerations

- **Lip-Sync**: MediaPipe processes at ~25-30 FPS on modern hardware
- **Audio Ducking**: Real-time capable using NumPy/SciPy
- **VFX Processing**: ~5-10 FPS for 1080p with multiple effects
- **Audio Mixing**: Real-time capable for up to 8+ tracks

## Troubleshooting

### Audio Ducking Not Working
- Ensure voice track has clear audio content
- Adjust `voice_threshold` parameter if needed
- Check attack/release times are reasonable

### Lip-Sync Issues
- Ensure good lighting in video
- Face must be clearly visible
- Use `process_video_for_lipsync` with debug output to verify

### Blender Script Errors
- Check Blender Python environment
- Verify file paths in script
- Ensure Blender version compatibility

## Future Enhancements

- Real-time Wav2Lip integration
- Advanced audio reactive VFX
- Machine learning-based scene generation
- Real-time preview system
- GPU acceleration for processing
- Cloud rendering support

## License

Part of Srijan Engine - Advanced AI Text-to-Movie Software

## Support

For issues or feature requests related to audio-visual processing:
1. Check integration_example.py for usage patterns
2. Review module docstrings
3. Check log output for detailed error messages

---

**Last Updated**: January 2026
**Version**: 2.0 (Advanced Audio-Visual Edition)
