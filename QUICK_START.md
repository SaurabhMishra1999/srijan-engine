# Srijan Engine - Quick Start Guide for Advanced Features

## Installation (5 minutes)

```bash
# Navigate to project root
cd e:\Srijan_Engine

# Install updated requirements
pip install -r requirements.txt

# Verify installation
python -c "import cv2, mediapipe, librosa, pydub; print('✓ All packages installed')"
```

## Quick Examples (Copy & Paste Ready)

### Example 1: Generate Emotional Voice (30 seconds)

```python
from src.audio.emotional_voice_engine import EmotionalVoiceEngine

engine = EmotionalVoiceEngine()

# Generate happy voice
audio = engine.generate_emotional_voice(
    text="Welcome to Saipooja Warehouse!",
    emotion="happy"
)

print(f"✓ Audio saved: {audio}")
```

### Example 2: Detect Lip-Sync from Video (1 minute)

```python
from src.audio.lip_sync_engine import LipSyncEngine

engine = LipSyncEngine()

# Analyze video and save debug output
frame_data = engine.process_video_for_lipsync(
    video_path="your_video.mp4",
    output_debug_path="debug_with_landmarks.mp4"
)

print(f"✓ Analyzed {len(frame_data)} frames")
print(f"✓ Debug video: debug_with_landmarks.mp4")
```

### Example 3: Apply Audio Ducking (2 minutes)

```python
from src.audio.audio_visual_merger import AudioVisualMerger

merger = AudioVisualMerger()

# Reduce music when voice is speaking
ducked = merger.apply_audio_ducking(
    voice_track_path="narration.wav",
    music_track_path="background_music.wav",
    output_path="music_with_ducking.wav",
    duck_amount_db=-15
)

print(f"✓ Ducked audio saved: {ducked}")
```

### Example 4: Apply Color Grading (1 minute)

```python
from src.blender.vfx_processor import VFXProcessor

vfx = VFXProcessor()

# Process video with cinematic color grading
config = {
    'color_grade': 'teal_orange',
    'grain': 0.05,
    'sharpness': 0.8
}

result = vfx.process_video_with_vfx(
    input_path="raw_video.mp4",
    output_path="graded_video.mp4",
    vfx_config=config
)

print(f"✓ Color graded video: {result}")
```

### Example 5: Create Warehouse Scene (2 minutes)

```python
from src.blender.warehouse_assets_manager import WarehouseAssetsManager

manager = WarehouseAssetsManager()

# Create scene
scene = manager.create_scene(
    scene_name="Warehouse Tour",
    scene_id="tour_001"
)

# Add assets
manager.add_asset_to_scene("tour_001", "container_truck_001", position=(0, 0, 0))
manager.add_asset_to_scene("tour_001", "forklift_001", position=(5, 0, 0))

# Export for Blender
manager.export_scene_config("tour_001", "scene.json")

# Generate setup script
manager.generate_blender_setup_script("tour_001", "setup.py")

print("✓ Scene created and exported")
```

### Example 6: Complete Workflow (5 minutes)

```python
from src.audio.emotional_voice_engine import EmotionalVoiceEngine
from src.audio.audio_visual_merger import AudioVisualMerger
from src.blender.warehouse_assets_manager import WarehouseAssetsManager

# 1. Generate narration
voice_engine = EmotionalVoiceEngine()
narration = voice_engine.generate_emotional_voice(
    text="This is the Saipooja Warehouse facility.",
    emotion="neutral"
)

# 2. Mix audio
merger = AudioVisualMerger()
merger.add_audio_track(narration, "Narration", volume=1.0)
mixed_audio = merger.mix_audio_tracks("final_audio.wav")

# 3. Setup scene
assets = WarehouseAssetsManager()
scene = assets.create_scene("Warehouse", "wh_001")
assets.add_asset_to_scene("wh_001", "container_truck_001")

# 4. Generate configs
assets.export_scene_config("wh_001", "scene.json")

print("✓ Complete workflow done!")
```

## Common Use Cases

### Use Case 1: Narrated Warehouse Tour

```python
# Generate emotional narration for different sections
sections = [
    ("Introduction", "excited", "Welcome to our state-of-the-art facility!"),
    ("Fleet", "neutral", "We operate 50 container trucks..."),
    ("Innovation", "happy", "Our automated systems are cutting-edge..."),
]

voice_engine = EmotionalVoiceEngine()
audio_paths = []

for section_name, emotion, text in sections:
    audio = voice_engine.generate_emotional_voice(
        text=text,
        emotion=emotion,
        filename=f"{section_name}_{emotion}.wav"
    )
    audio_paths.append(audio)

print(f"✓ Generated {len(audio_paths)} narration sections")
```

### Use Case 2: Professional Video with Effects

```python
from src.blender.vfx_processor import VFXProcessor

vfx = VFXProcessor()

# Professional cinematic processing
effects = {
    'color_grade': 'teal_orange',      # Cinematic look
    'grain': 0.03,                      # Subtle film grain
    'sharpness': 1.2,                   # Enhanced details
    'distortion': 0.01                  # Lens effect
}

polished_video = vfx.process_video_with_vfx(
    input_path="raw_render.mp4",
    output_path="final_video.mp4",
    vfx_config=effects
)
```

### Use Case 3: Multi-Asset Warehouse Scene

```python
from src.blender.warehouse_assets_manager import WarehouseAssetsManager, AssetType

manager = WarehouseAssetsManager()

# Create rich scene
scene = manager.create_scene("Full Warehouse", "full_001")

# Add multiple assets with positioning
positions = {
    "container_truck_001": (0, 0, 0),
    "forklift_001": (8, 0, 0),
    "forklift_001": (8, 5, 0),
    "warehouse_shelf_001": (-10, 0, 0),
    "pallet_001": (3, 3, 0),
}

for asset_id, pos in positions.items():
    manager.add_asset_to_scene("full_001", asset_id, position=pos)

# Export
manager.export_scene_config("full_001", "warehouse_full.json")
```

### Use Case 4: Blender Particle Effects

```python
from src.blender.vfx_processor import BlenderParticleEffects

fx = BlenderParticleEffects()

# Generate effect scripts
fx.generate_dust_particles_script(
    "dust.py",
    intensity=0.8,
    particle_count=5000
)

fx.generate_vehicle_effects_script(
    "truck_fx.py",
    vehicle_type="truck",
    intensity=0.7
)

# Run scripts in Blender:
# blender scene.blend -b -P dust.py
# blender scene.blend -b -P truck_fx.py
```

## Debugging Tips

### Enable Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

# Now all modules will show detailed logs
```

### Check Processing Logs

```python
merger = AudioVisualMerger()
# ... do processing ...

logs = merger.get_processing_log()
for step in logs:
    print(step)
```

### Verify Assets

```python
manager = WarehouseAssetsManager()

# List all assets
assets = manager.list_all_assets()
for asset in assets:
    print(f"{asset['name']}: {asset['asset_type']}")

# Get statistics
stats = manager.get_asset_statistics()
print(f"Total: {stats['total_assets']}")
```

## Performance Tips

1. **Audio Processing**: Process in batches of 16 samples for optimal speed
2. **Video Effects**: Process at 720p first, upscale for final output
3. **Lip-Sync**: Use pre-detected landmarks if processing same video multiple times
4. **Particle Effects**: Generate Blender scripts rather than computing in Python

## Output Locations

- Voice files: `assets/audio/`
- Video output: `output/`
- Scene configs: `output/scene_configs/`
- Blender scripts: `output/blender_scripts/`
- Processing reports: `output/`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Module not found" | Run `pip install -r requirements.txt` |
| Audio too quiet | Increase `volume` parameter to > 1.0 |
| Ducking too aggressive | Increase `attack_ms` and `release_ms` |
| Landmarks not detecting | Ensure face is visible and well-lit |
| Blender script errors | Check Python version compatibility |
| VFX too slow | Process at lower resolution first |

## Next Steps

1. **Integrate into GUI**: Update `src/gui/app.py` to use new modules
2. **Create Templates**: Build reusable scene templates for common scenarios
3. **Setup Rendering**: Configure Blender for batch rendering
4. **Optimize**: Profile performance and optimize for your hardware
5. **Deploy**: Package for distribution with pre-built assets

## Example Project Structure

```
projects/
├── warehouse_tour_001/
│   ├── script.txt          # Original script
│   ├── narration/
│   │   ├── intro.wav
│   │   ├── tour.wav
│   │   └── conclusion.wav
│   ├── scene_config.json   # Asset positions
│   ├── setup.py            # Blender setup script
│   ├── render_output.mp4   # From Blender
│   ├── effects.mp4         # VFX applied
│   └── final_video.mp4     # With audio
```

## Quick Command Reference

```bash
# Generate all components for a project
python src/integration_example.py

# Run individual examples
python -c "from src.audio.emotional_voice_engine import EmotionalVoiceEngine; EmotionalVoiceEngine().generate_emotional_voice('Hello', 'happy')"

# Check available assets
python -c "from src.blender.warehouse_assets_manager import WarehouseAssetsManager; print(WarehouseAssetsManager().list_all_assets())"
```

---

**Ready to create amazing warehouse videos! 🎬🎙️**

For detailed documentation, see: [AUDIO_VISUAL_FEATURES.md](AUDIO_VISUAL_FEATURES.md)
