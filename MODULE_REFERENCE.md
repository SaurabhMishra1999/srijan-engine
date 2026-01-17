# Module Reference Guide - Srijan Engine Advanced Features

## Quick Navigation

- [Audio Modules](#audio-modules)
- [VFX Modules](#vfx-modules)
- [Asset Management](#asset-management)
- [API Reference](#api-reference)

---

## Audio Modules

### 1. voice_engine.py
**Location**: `src/audio/voice_engine.py`  
**Purpose**: Basic voice recording and TTS generation  
**Status**: Enhanced with logging and type hints

#### Class: VoiceEngine

```python
class VoiceEngine:
    def __init__(audio_dir: Optional[str] = None)
    def record_voice(duration: float = 5, filename: Optional[str] = None, 
                     samplerate: int = 44100) -> str
    def generate_ai_voice(text: str, filename: Optional[str] = None,
                         rate: int = 150, volume: float = 1.0) -> str
```

#### Quick Usage:
```python
from src.audio.voice_engine import VoiceEngine

engine = VoiceEngine()
# Record voice
voice = engine.record_voice(duration=5, filename="my_voice.wav")
# Generate TTS
tts = engine.generate_ai_voice("Hello world!", filename="hello.wav")
```

---

### 2. emotional_voice_engine.py
**Location**: `src/audio/emotional_voice_engine.py`  
**Purpose**: Advanced TTS with emotional expression  
**Dependencies**: pyttsx3, librosa, soundfile, pydub  
**Lines of Code**: 420+

#### Class: EmotionalVoiceEngine

```python
class EmotionalVoiceEngine:
    def __init__(audio_dir: Optional[str] = None)
    
    # Core methods
    def generate_emotional_voice(text: str, emotion: str = 'neutral',
                                voice_variant: str = 'voice_0',
                                filename: Optional[str] = None) -> str
    
    def blend_emotions(text: str, emotions: List[Tuple[str, float]],
                      filename: Optional[str] = None) -> str
    
    def add_audio_effects(filepath: str, effects: List[str],
                         output_path: Optional[str] = None) -> str
    
    # Utility methods
    def get_available_emotions() -> List[str]
    def get_available_voices() -> List[str]
    def validate_emotion(emotion: str) -> bool
```

#### Emotion Presets:
```python
EMOTION_PRESETS = {
    'neutral':   {'pitch': 1.0,  'rate': 150, 'volume': 1.0},
    'happy':     {'pitch': 1.2,  'rate': 170, 'volume': 1.1},
    'sad':       {'pitch': 0.8,  'rate': 120, 'volume': 0.9},
    'angry':     {'pitch': 0.95, 'rate': 180, 'volume': 1.15},
    'excited':   {'pitch': 1.3,  'rate': 200, 'volume': 1.2},
    'concerned': {'pitch': 0.9,  'rate': 140, 'volume': 0.95},
    'whisper':   {'pitch': 0.7,  'rate': 100, 'volume': 0.5},
}
```

#### Quick Usage:
```python
from src.audio.emotional_voice_engine import EmotionalVoiceEngine

engine = EmotionalVoiceEngine()

# Generate with emotion
happy = engine.generate_emotional_voice("Great news!", emotion="happy")
sad = engine.generate_emotional_voice("Bad news...", emotion="sad")

# Blend emotions
blended = engine.blend_emotions(
    text="This is complex.",
    emotions=[("concerned", 0.6), ("neutral", 0.4)]
)

# Add effects
enhanced = engine.add_audio_effects(
    filepath=happy,
    effects=['normalize', 'compress']
)
```

---

### 3. lip_sync_engine.py
**Location**: `src/audio/lip_sync_engine.py`  
**Purpose**: Facial animation and lip-sync detection  
**Dependencies**: cv2, mediapipe, numpy, librosa  
**Lines of Code**: 370+

#### Class: LipSyncEngine

```python
class LipSyncEngine:
    def __init__()
    
    def detect_face_landmarks(frame: np.ndarray) -> Optional[dict]
    def extract_mouth_region(frame: np.ndarray, landmarks: dict,
                            padding: int = 10) -> Optional[np.ndarray]
    def calculate_mouth_openness(landmarks: dict) -> float
    def calculate_mouth_shape(landmarks: dict) -> str
    def apply_wav2lip_effect(video_path: str, audio_path: str,
                            output_path: str, batch_size: int = 64) -> bool
    def draw_face_landmarks(frame: np.ndarray, landmarks: dict) -> np.ndarray
    def process_video_for_lipsync(video_path: str,
                                 output_debug_path: Optional[str] = None) -> List[dict]
```

#### Mouth Shapes (Visemes):
```python
'closed'  # Lips closed, no opening
'open'    # Mouth wide open
'rounded' # Lips rounded, small opening
'spread'  # Wide horizontal mouth
```

#### Quick Usage:
```python
from src.audio.lip_sync_engine import LipSyncEngine

engine = LipSyncEngine()

# Process video
frame_data = engine.process_video_for_lipsync(
    video_path="character_video.mp4",
    output_debug_path="debug_with_landmarks.mp4"
)

# Get mouth metrics per frame
for frame in frame_data:
    print(f"Frame {frame['frame_id']}: openness={frame['mouth_openness']:.2f}, "
          f"shape={frame['mouth_shape']}")
```

---

### 4. audio_visual_merger.py
**Location**: `src/audio/audio_visual_merger.py`  
**Purpose**: Multi-track audio mixing, visual effects, and video merging  
**Dependencies**: moviepy, librosa, scipy, pydub, cv2  
**Lines of Code**: 850+

#### Main Classes:

```python
class AudioTrack:
    path: str
    name: str
    duration: float
    volume: float = 1.0
    start_time: float = 0.0
    fade_in: float = 0.0
    fade_out: float = 0.0

class VisualEffect:
    effect_type: str  # 'color_grade', 'grain', 'blur', 'sharpen', 'vignette'
    intensity: float
    start_frame: int
    end_frame: int
    parameters: Dict = None

class AudioVisualMerger:
    def __init__(output_dir: Optional[str] = None,
                temp_dir: Optional[str] = None)
    
    # Audio methods
    def add_audio_track(audio_path: str, name: str, volume: float = 1.0,
                       start_time: float = 0.0, fade_in: float = 0.0,
                       fade_out: float = 0.0) -> AudioTrack
    
    def apply_audio_ducking(voice_track_path: str, music_track_path: str,
                           output_path: str, duck_amount_db: float = -12,
                           attack_ms: float = 100, release_ms: float = 200) -> str
    
    def mix_audio_tracks(output_path: str, normalize: bool = True) -> str
    
    # Visual effect methods
    def add_visual_effect(effect_type: str, intensity: float,
                         start_frame: int, end_frame: int,
                         parameters: Optional[Dict] = None) -> VisualEffect
    
    def apply_color_grading(frame: np.ndarray, intensity: float,
                           color_temp: str = 'warm') -> np.ndarray
    
    def apply_cinematic_grain(frame: np.ndarray, intensity: float,
                             grain_size: int = 2) -> np.ndarray
    
    def apply_vignette(frame: np.ndarray, intensity: float) -> np.ndarray
    
    def process_video_with_effects(input_video: str,
                                  output_video: str) -> str
    
    # Merge methods
    def merge_video_and_audio(video_path: str, audio_path: str,
                             output_path: str,
                             video_duration: Optional[float] = None) -> str
    
    def get_processing_log() -> List[str]
    def export_processing_report(report_path: Optional[str] = None) -> str
```

#### Color Grading Styles:
```python
'teal_orange'   # Cinema standard (teal shadows, orange highlights)
'blue_yellow'   # Cool shadows, warm highlights
'desaturated'   # Reduced saturation for drama
'warm'          # Vintage warm aesthetic
```

#### Quick Usage:
```python
from src.audio.audio_visual_merger import AudioVisualMerger

merger = AudioVisualMerger()

# Add tracks
mixer.add_audio_track("dialogue.wav", "Dialogue", volume=1.0)
mixer.add_audio_track("music.wav", "Music", volume=0.8, fade_in=0.5)

# Apply ducking
ducked = mixer.apply_audio_ducking(
    voice_track_path="dialogue.wav",
    music_track_path="music.wav",
    output_path="music_ducked.wav",
    duck_amount_db=-15
)

# Mix and merge
audio = mixer.mix_audio_tracks("final_audio.wav")
final = mixer.merge_video_and_audio(
    video_path="video.mp4",
    audio_path="final_audio.wav",
    output_path="final_output.mp4"
)

# Get report
mixer.export_processing_report("report.json")
```

---

## VFX Modules

### 5. vfx_processor.py
**Location**: `src/blender/vfx_processor.py`  
**Purpose**: Visual effects processing and Blender script generation  
**Dependencies**: cv2, numpy, PIL, os  
**Lines of Code**: 700+

#### Classes:

```python
class VFXProcessor:
    def __init__()
    
    # Color grading
    def apply_lut_color_grade(frame: np.ndarray, lut_path: str) -> np.ndarray
    def apply_cinematic_color_grade(frame: np.ndarray,
                                   style: str = 'teal_orange') -> np.ndarray
    
    # Film effects
    def apply_film_grain(frame: np.ndarray, grain_intensity: float = 0.05,
                        grain_color: bool = False) -> np.ndarray
    def apply_lens_distortion(frame: np.ndarray, distortion: float = 0.05) -> np.ndarray
    
    # Motion effects
    def apply_motion_blur(frame: np.ndarray, direction: str = 'horizontal',
                         blur_amount: int = 15) -> np.ndarray
    def apply_chromatic_aberration(frame: np.ndarray, offset: int = 3) -> np.ndarray
    
    # Detail enhancement
    def apply_unsharp_mask(frame: np.ndarray, amount: float = 1.0,
                          radius: int = 1, threshold: int = 0) -> np.ndarray
    def apply_edge_enhance(frame: np.ndarray, strength: float = 1.0) -> np.ndarray
    
    # Batch processing
    def process_video_with_vfx(input_path: str, output_path: str,
                              vfx_config: Dict) -> str

class BlenderParticleEffects:
    def __init__(blender_python_path: Optional[str] = None)
    
    def generate_dust_particles_script(output_script: str, intensity: float = 1.0,
                                      particle_count: int = 5000) -> str
    def generate_smoke_effects_script(output_script: str,
                                     intensity: float = 1.0) -> str
    def generate_fire_effects_script(output_script: str,
                                    intensity: float = 1.0) -> str
    def generate_vehicle_effects_script(output_script: str, vehicle_type: str = 'truck',
                                       intensity: float = 1.0) -> str
```

#### Quick Usage:
```python
from src.blender.vfx_processor import VFXProcessor, BlenderParticleEffects

vfx = VFXProcessor()

# Process video
config = {
    'color_grade': 'teal_orange',
    'grain': 0.05,
    'sharpness': 1.0,
    'distortion': 0.02
}

result = vfx.process_video_with_vfx(
    input_path="raw.mp4",
    output_path="processed.mp4",
    vfx_config=config
)

# Generate Blender scripts
fx = BlenderParticleEffects()
fx.generate_dust_particles_script("dust.py", intensity=0.8)
fx.generate_vehicle_effects_script("truck.py", vehicle_type="truck")
```

---

## Asset Management

### 6. warehouse_assets_manager.py
**Location**: `src/blender/warehouse_assets_manager.py`  
**Purpose**: 3D asset inventory and scene management  
**Dependencies**: json, dataclasses, enum  
**Lines of Code**: 650+

#### Enums & Data Classes:

```python
class AssetType(Enum):
    FORKLIFT = "forklift"
    MEDICINE_BOX = "medicine_box"
    CONTAINER_TRUCK = "container_truck"
    SHELF = "shelf"
    PALLET = "pallet"
    WAREHOUSE_STRUCTURE = "warehouse_structure"
    LIGHTING = "lighting"
    CAMERA = "camera"
    PARTICLE_SYSTEM = "particle_system"

@dataclass
class Asset3D:
    asset_id: str
    name: str
    asset_type: AssetType
    model_path: str
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    texture_path: Optional[str] = None
    material_name: Optional[str] = None
    physics_enabled: bool = False
    animation_path: Optional[str] = None
    metadata: Dict = None

@dataclass
class WarehouseScene:
    scene_name: str
    scene_id: str
    description: str
    assets: List[Asset3D]
    duration: float = 5.0
    frame_rate: int = 30
    resolution: Tuple[int, int] = (1920, 1080)
    lighting_config: Dict = None
    camera_config: Dict = None
    physics_enabled: bool = True
```

#### Main Class:

```python
class WarehouseAssetsManager:
    def __init__(assets_dir: Optional[str] = None)
    
    # Asset management
    def register_asset(asset: Asset3D) -> bool
    def get_asset(asset_id: str) -> Optional[Asset3D]
    def get_assets_by_type(asset_type: AssetType) -> List[Asset3D]
    def update_asset(asset_id: str, **kwargs) -> bool
    
    # Scene management
    def create_scene(scene_name: str, scene_id: str,
                    description: str = "") -> WarehouseScene
    def add_asset_to_scene(scene_id: str, asset_id: str,
                          position: Optional[Tuple[float, float, float]] = None,
                          rotation: Optional[Tuple[float, float, float]] = None,
                          scale: Optional[Tuple[float, float, float]] = None) -> bool
    def remove_asset_from_scene(scene_id: str, asset_id: str) -> bool
    def get_scene(scene_id: str) -> Optional[WarehouseScene]
    
    # Export and generation
    def export_scene_config(scene_id: str, output_path: str) -> bool
    def generate_blender_setup_script(scene_id: str,
                                     output_script: str) -> bool
    
    # Reporting
    def list_all_assets() -> List[Dict]
    def list_all_scenes() -> List[Dict]
    def get_asset_statistics() -> Dict
```

#### Pre-loaded Assets:
```
1. forklift_001 - Standard Forklift (2500kg capacity)
2. medicine_box_001 - Medical Boxes (cardboard, stackable)
3. container_truck_001 - 40ft Container Truck (20000kg)
4. warehouse_shelf_001 - Industrial Shelf (2.5m height, 4 shelves)
5. pallet_001 - Wooden Pallet (Euro pallet, 1200x800mm)
```

#### Quick Usage:
```python
from src.blender.warehouse_assets_manager import WarehouseAssetsManager

manager = WarehouseAssetsManager()

# Create scene
scene = manager.create_scene("Warehouse Tour", "tour_001")

# Add assets
manager.add_asset_to_scene("tour_001", "container_truck_001", position=(0, 0, 0))
manager.add_asset_to_scene("tour_001", "forklift_001", position=(5, 0, 0))

# Export
manager.export_scene_config("tour_001", "scene.json")
manager.generate_blender_setup_script("tour_001", "setup.py")

# Statistics
stats = manager.get_asset_statistics()
print(f"Total assets: {stats['total_assets']}")
```

---

## API Reference

### Audio Ducking Parameters

```python
apply_audio_ducking(
    voice_track_path: str,      # Path to voice/dialogue
    music_track_path: str,      # Path to background music
    output_path: str,           # Where to save ducked audio
    duck_amount_db: float = -12,# Reduction amount (negative)
    attack_ms: float = 100,     # Attack time in milliseconds
    release_ms: float = 200     # Release time in milliseconds
) -> str
```

### VFX Configuration Dictionary

```python
vfx_config = {
    'color_grade': 'teal_orange',  # Style: teal_orange, blue_yellow, desaturated, warm
    'grain': 0.05,                 # 0.0 - 1.0 (intensity)
    'sharpness': 1.0,              # 0.0 - 2.0
    'distortion': 0.02,            # 0.0 - 0.1 (barrel/pincushion)
    'chromatic': 3                 # pixels (RGB separation)
}
```

### Emotional Voice Parameters

```python
generate_emotional_voice(
    text: str,                 # Text to synthesize
    emotion: str = 'neutral',  # happy, sad, angry, excited, concerned, whisper
    voice_variant: str = 'voice_0',  # voice_0, voice_1, etc
    filename: Optional[str] = None   # Output filename
) -> str  # Returns path to generated audio
```

### Scene Creation

```python
create_scene(
    scene_name: str,        # Name of scene
    scene_id: str,          # Unique identifier
    description: str = ""   # Description
) -> WarehouseScene
```

---

## File Locations

```
assets/
├── audio/               # Generated voice files
├── models/              # 3D model files
└── environments/        # Environment assets

output/
├── scene_configs/       # JSON scene configurations
├── blender_scripts/     # Generated Blender .py files
└── *_report.json        # Processing reports
```

---

## Dependencies Summary

| Module | Dependencies |
|--------|--------------|
| voice_engine | pyttsx3, sounddevice, soundfile |
| emotional_voice_engine | pyttsx3, librosa, soundfile, pydub, numpy, scipy |
| lip_sync_engine | cv2, mediapipe, numpy, librosa |
| audio_visual_merger | moviepy, librosa, scipy, pydub, cv2, numpy |
| vfx_processor | cv2, numpy, PIL, os |
| warehouse_assets_manager | json, dataclasses, enum |

---

## Troubleshooting

### Module Import Errors
```python
# Ensure all requirements are installed
pip install -r requirements.txt

# Check installation
python -c "from src.audio.emotional_voice_engine import EmotionalVoiceEngine"
```

### Audio Issues
```python
# Check available voices
engine = EmotionalVoiceEngine()
print(engine.get_available_voices())

# Verify emotion
if not engine.validate_emotion("happy"):
    print("Use one of:", engine.get_available_emotions())
```

### Video Processing
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check video format
cap = cv2.VideoCapture("video.mp4")
print(f"FPS: {cap.get(cv2.CAP_PROP_FPS)}")
print(f"Size: {cap.get(cv2.CAP_PROP_FRAME_WIDTH)}x{cap.get(cv2.CAP_PROP_FRAME_HEIGHT)}")
```

---

## Performance Tips

1. **Process at lower resolution first**: 720p → 1080p
2. **Use batch processing**: Better GPU utilization
3. **Cache computed values**: Reuse landmarks, metadata
4. **Parallelize when possible**: Audio and VFX processing
5. **Monitor memory**: Stream video instead of loading entirely

---

**For comprehensive examples, see**: `src/integration_example.py`  
**For detailed documentation**: `AUDIO_VISUAL_FEATURES.md`  
**For quick start**: `QUICK_START.md`
