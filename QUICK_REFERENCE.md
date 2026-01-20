# 🚀 Quick Reference Guide - Srijan Engine

## Start Here

### Web Interface (Easiest)
```bash
python web_app.py
# Open: http://localhost:5000
```

### Desktop App
```bash
python -m src.gui.main
```

---

## Complete Pipeline in Code

```python
# 1. Parse Script
from src.ai.script_processor import ScriptProcessor
processor = ScriptProcessor()
config = processor.parse_script_to_scenes("Your script...")

# 2. Generate Audio
from src.audio.emotional_voice_engine import EmotionalVoiceEngine
engine = EmotionalVoiceEngine()
audio = engine.generate_emotional_voice("Text...", emotion="happy")

# 3. Render Video
from src.blender.renderer import BlenderRenderer
renderer = BlenderRenderer()
video = renderer.render_scene_to_video(
    script="Description...",
    output_path="output/movie.mp4",
    duration=10
)

# 4. Merge Everything
from src.audio.audio_visual_merger import AudioVisualMerger
merger = AudioVisualMerger()
merger.add_visual_effect('color_grade', 0.7, 0, 9999)
merger.add_visual_effect('grain', 0.05, 0, 9999)
final = merger.merge_video_and_audio(video, audio, "output/final.mp4")
```

---

## Available Narration Emotions

```
1. happy     - Upbeat, positive, energetic
2. sad       - Somber, melancholic
3. angry     - Intense, aggressive
4. excited   - Enthusiastic, fast
5. concerned - Worried, cautious
6. whisper   - Soft, intimate
7. neutral   - Professional, standard
```

---

## API Endpoint

```bash
curl -X POST http://localhost:5000/api/generate-movie \
  -H "Content-Type: application/json" \
  -d '{
    "script": "A person walks through a warehouse",
    "narration_style": "happy",
    "duration": 30,
    "enable_color_grade": true,
    "enable_film_grain": true,
    "enable_subtitles": true
  }'
```

---

## Output Files

All files saved to: `output/`

```
movie_[timestamp].mp4       ← Final video (1920x1080, H.264)
narration_[timestamp].wav   ← Audio (16-bit, 44.1kHz)
subtitles_[timestamp].srt   ← Captions (SRT format)
```

---

## Testing

```bash
# Run complete pipeline test
python test_complete_pipeline.py

# Expected: 6/6 tests pass
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No video file | Install ffmpeg: `pip install imageio-ffmpeg` |
| Blender not found | Install from blender.org or system will use test video |
| Audio not generating | Install: `pip install pyttsx3` |
| Memory error | Reduce duration or resolution |

---

## Configuration Files

- **Web**: `web_app.py` - Flask app settings
- **GUI**: `src/gui/main.py` - Desktop interface
- **Rendering**: `src/blender/renderer.py` - Blender settings
- **Voice**: `src/audio/emotional_voice_engine.py` - TTS settings

---

## Key Classes

| Class | Module | Purpose |
|-------|--------|---------|
| ScriptProcessor | src/ai/script_processor.py | Parse script → scenes |
| BlenderRenderer | src/blender/renderer.py | Render 3D to video |
| EmotionalVoiceEngine | src/audio/emotional_voice_engine.py | Generate narration |
| AudioVisualMerger | src/audio/audio_visual_merger.py | Merge audio + video |
| SceneGenerator | src/blender/scene_generator.py | Config → Blender file |

---

## Documentation

- `COMPLETE_USAGE_GUIDE.md` - Full API documentation
- `COMPLETION_SUMMARY.md` - What was completed
- `README.md` - Project overview

---

## Project Status

✅ **COMPLETE & PRODUCTION READY**

- All TODOs resolved
- Full pipeline implemented
- Comprehensive error handling
- Multiple interfaces
- Professional quality output

---

**Last Updated:** January 18, 2026
