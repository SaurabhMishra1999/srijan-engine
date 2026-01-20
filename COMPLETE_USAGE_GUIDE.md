# Srijan Engine - Complete Video Generation Pipeline

## 📋 Overview

The Srijan Engine is now a **complete, production-ready system** for generating movies from text scripts with:
- ✅ AI-powered script parsing → 3D scenes
- ✅ Emotional voice narration generation
- ✅ Professional video rendering with VFX
- ✅ Audio-visual synchronization
- ✅ Subtitle generation

## 🚀 Quick Start

### Option 1: Web Interface (Recommended)
```bash
python web_app.py
```
Then open http://localhost:5000 in your browser and:
1. Enter your script in the text area
2. Choose narration style (happy, sad, excited, etc.)
3. Click "Generate Movie"
4. Download the final video

### Option 2: Python GUI
```bash
python -m src.gui.main
```
- Paste or write your script
- Click "Generate Movie"
- Check `output/` folder for results

### Option 3: Direct API Call
```python
import requests

response = requests.post('http://localhost:5000/api/generate-movie', json={
    'script': 'Your script here...',
    'narration_style': 'happy',
    'duration': 30,
    'enable_color_grade': True,
    'enable_film_grain': True,
    'enable_subtitles': True
})

result = response.json()
print(f"Video: {result['video_file']}")
print(f"Narration: {result['narration_file']}")
print(f"Subtitles: {result['subtitle_file']}")
```

## 🔧 System Components

### 1. **Script Processor** (`src/ai/script_processor.py`)
Converts narrative scripts into structured 3D scene configurations:
```python
from src.ai.script_processor import ScriptProcessor

processor = ScriptProcessor()
config = processor.parse_script_to_scenes("""
    A person walks through a warehouse.
    The lighting is soft and natural.
    Wide camera angle showing the full room.
""")

# Returns:
# {
#   'scenes': [
#     {
#       'description': '...',
#       'duration': 5,
#       'camera': {'angle': 'wide', 'position': (0, -10, 5)},
#       'lighting': 'soft',
#       'objects': [...]
#     }
#   ]
# }
```

**Features:**
- Detects scene descriptions automatically
- Identifies camera angles (wide, close-up, overhead, side)
- Extracts lighting preferences (soft, hard, dramatic, natural)
- Extracts objects and characters
- Estimates scene duration

### 2. **Emotional Voice Engine** (`src/audio/emotional_voice_engine.py`)
Generates narration with emotional expression:
```python
from src.audio.emotional_voice_engine import EmotionalVoiceEngine

engine = EmotionalVoiceEngine()

# Generate with different emotions
audio_file = engine.generate_emotional_voice(
    text="Your script text here",
    emotion="happy"  # or: sad, angry, excited, concerned, whisper, neutral
)
```

**Features:**
- 7 emotional presets
- Dynamic pitch shifting
- Speech rate adjustment
- Voice effect blending
- Audio normalization

### 3. **Blender Renderer** (`src/blender/renderer.py`)
Renders 3D scenes to video:
```python
from src.blender.renderer import BlenderRenderer

renderer = BlenderRenderer()
video_file = renderer.render_scene_to_video(
    script="Scene description...",
    output_path="output/movie.mp4",
    duration=10,
    fps=30,
    resolution="1920x1080"
)
```

**Features:**
- Automatic Blender detection
- Fallback to simple test video if Blender unavailable
- Configurable resolution and frame rate
- Support for multiple scenes
- Professional render settings

### 4. **Scene Generator** (`src/blender/scene_generator.py`)
Converts configuration to Blender scenes:
```python
from src.blender.scene_generator import SceneGenerator

generator = SceneGenerator()
blend_file = generator.create_scene_from_config({
    'scenes': [...],
    'global_config': {'fps': 30, 'resolution': '1920x1080'}
})
```

### 5. **Audio-Visual Merger** (`src/audio/audio_visual_merger.py`)
Combines audio, video, and effects:
```python
from src.audio.audio_visual_merger import AudioVisualMerger

merger = AudioVisualMerger()

# Add audio tracks
merger.add_audio_track('narration.wav', 'Narration', volume=1.0)
merger.add_audio_track('music.wav', 'Music', volume=0.5, fade_in=2, fade_out=2)

# Apply visual effects
merger.add_visual_effect('color_grade', 0.7, 0, 9999, {'color_temp': 'warm'})
merger.add_visual_effect('grain', 0.05, 0, 9999)
merger.add_visual_effect('vignette', 0.3, 0, 9999)

# Process and merge
mixer.process_video_with_effects('input.mp4', 'with_effects.mp4')
final = mixer.merge_video_and_audio('with_effects.mp4', 'narration.wav', 'final.mp4')
```

## 📁 Output Files

Generated files are saved to `output/` folder:

```
output/
├── movie_1705123456.789.mp4          ← Final video with audio & effects
├── narration_1705123456.789.wav      ← AI-generated narration
├── subtitles_1705123456.789.srt      ← Subtitle file
├── movie_with_vfx_1705123456.789.mp4 ← Video with effects (intermediate)
└── final_audio.wav                    ← Mixed audio track
```

## 🎬 Video Generation Flow

```
User Script
    ↓
[Script Processor] → Scene Configuration
    ↓
[Scene Generator] → Blender .blend file
    ↓
[Blender Renderer] → Video Frames (MP4)
    ├─→ [Audio-Visual Merger]
    │   ├─→ [Emotional Voice Engine] → Narration WAV
    │   ├─→ Apply VFX Effects
    │   └─→ Merge Audio + Video
    ↓
[Final Video] with Audio + Subtitles + Effects
    ↓
output/movie_[timestamp].mp4 ✅
```

## 🛠️ Configuration

### Web App Settings (`web_app.py`)
```python
# Max file upload size
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Output folder
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')

# Blender path (auto-detected, can override)
BLENDER_PATH = r"e:\Srijan_Engine\blender_portable\5.0\blender.exe"
```

### Render Settings
```python
# In renderer.py, modify render settings:
scene.render.fps = 30                          # Frame rate
scene.render.resolution_x = 1920               # Width
scene.render.resolution_y = 1080               # Height
scene.render.engine = 'BLENDER_EEVEE'         # Render engine
```

## 📊 Testing

Run the complete pipeline test:
```bash
python test_complete_pipeline.py
```

This will test:
- ✅ Script parsing
- ✅ Voice generation
- ✅ Audio-visual merging
- ✅ Blender availability
- ✅ Scene generation
- ✅ Complete flow

## 🐛 Troubleshooting

### Video file not created
- Check if ffmpeg is installed: `ffmpeg -version`
- Install: `pip install imageio-ffmpeg`

### Blender not found
- Install Blender from https://www.blender.org/download/
- Or use portable version at `blender_portable/5.0/blender.exe`
- System will fallback to test video if unavailable

### Audio not generating
- Install: `pip install pyttsx3` or `pip install gtts`
- Check `src/audio/emotional_voice_engine.py` for supported TTS engines

### Memory issues
- Reduce video resolution in settings
- Use shorter script duration
- Increase available RAM

## 📦 Dependencies

```bash
# Core dependencies
pip install flask flask-cors customtkinter

# Audio processing
pip install pydub librosa scipy soundfile

# Video processing
pip install opencv-python moviepy imageio-ffmpeg

# AI/ML (optional)
pip install torch torchvision

# Text-to-speech
pip install pyttsx3 gtts

# Web streaming
pip install python-socketio python-engineio
```

## 🎨 Narration Styles (Emotions)

1. **happy** - Upbeat, energetic, positive tone
2. **sad** - Somber, melancholic tone
3. **angry** - Intense, aggressive tone
4. **excited** - Enthusiastic, fast-paced tone
5. **concerned** - Worried, cautious tone
6. **whisper** - Soft, intimate tone
7. **neutral** - Standard, professional tone

## 🌟 Advanced Usage

### Custom Scene Configuration
```python
from src.blender.scene_generator import SceneGenerator

custom_config = {
    'scenes': [
        {
            'id': 1,
            'description': 'A warehouse entrance',
            'duration': 5,
            'camera': {
                'angle': 'wide',
                'position': (0, -15, 5)
            },
            'lighting': 'soft',
            'background': 'warehouse',
            'objects': [
                {
                    'name': 'character',
                    'type': 'character',
                    'position': (0, 0, 0),
                    'scale': (1, 1, 1)
                }
            ]
        }
    ],
    'global_config': {
        'fps': 30,
        'resolution': '1920x1080',
        'color_space': 'sRGB'
    }
}

generator = SceneGenerator()
blend_file = generator.create_scene_from_config(custom_config)
```

### Multiple Audio Tracks
```python
from src.audio.audio_visual_merger import AudioVisualMerger

merger = AudioVisualMerger()

# Main narration
merger.add_audio_track('narration.wav', 'Narration', volume=1.0, fade_in=1, fade_out=1)

# Background music
merger.add_audio_track('music.wav', 'Music', volume=0.4, start_time=0, fade_out=2)

# Sound effects
merger.add_audio_track('sfx.wav', 'Effects', volume=0.6, start_time=2)

# Mix all
final_audio = merger.mix_audio_tracks('output/mixed_audio.wav', normalize=True)
```

## 📝 Subtitle Format

Subtitles are generated in SRT format:
```
1
00:00:00,000 --> 00:00:03,000
First line of script...

2
00:00:03,000 --> 00:00:06,000
Second line of script...
```

## 🔗 API Endpoints

### Generate Movie
```
POST /api/generate-movie
Content-Type: application/json

{
  "script": "Your script text...",
  "narration_style": "happy",
  "duration": 30,
  "enable_color_grade": true,
  "enable_film_grain": true,
  "enable_subtitles": true
}
```

### List Output Files
```
GET /api/output-files
```

### Download File
```
GET /download/<filename>
```

## ✨ Features Summary

| Feature | Status | Details |
|---------|--------|---------|
| Script Parsing | ✅ | AI-powered scene extraction |
| Voice Generation | ✅ | 7 emotional presets |
| 3D Rendering | ✅ | Blender integration |
| VFX Effects | ✅ | Color grading, grain, vignette |
| Audio Mixing | ✅ | Multi-track with ducking |
| Subtitle Gen | ✅ | Auto SRT generation |
| Web Interface | ✅ | Flask-based UI |
| GUI Interface | ✅ | CustomTkinter desktop app |
| Video Export | ✅ | MP4 H.264 codec |

## 📞 Support

For issues or questions:
1. Check `test_complete_pipeline.py` for diagnostics
2. Review logs in terminal/console
3. Check output folder for generated files
4. Verify all dependencies are installed

## 📄 License

Part of the Srijan Engine project - AI-powered video generation platform.
