# 📹 Video Output Location Guide

## Kahan Dikhenge Generated Videos?

### 1. **Output Folder Location**
```
e:\Srijan_Engine\output\
```

### 2. **Generated Files Structure**

When you generate a movie using AI Script Engine, 3 files create hoti hain:

```
output/
├── movie_1768690458.043417.mp4      ← 🎬 FINAL VIDEO (Main output)
├── narration_1768690458.042477.wav  ← 🎤 NARRATION AUDIO
└── subtitles_1768690458.044422.srt  ← 📝 SUBTITLE FILE
```

### 3. **File Types Explained**

| File Type | Purpose | Size | Format |
|-----------|---------|------|--------|
| `.mp4` | Final movie with all effects | ~50-200MB | MPEG-4 Video |
| `.wav` | AI-generated narration audio | ~5-15MB | Uncompressed Audio |
| `.srt` | Subtitle file for timing & text | ~1-5KB | Text (SubRip) |

### 4. **Browser Mein Kaise Dekhenge?**

Option A: **Direct Download from Web UI**
```
1. http://localhost:5000 (Flask server)
2. AI Script Engine modal open karo
3. Script dalo
4. "Generate Movie" click karo
5. Status mein output path dikhega
6. Click karo download icon se
```

Option B: **File Explorer Mein Open Karo**
```
1. Windows Explorer open karo
2. Path: e:\Srijan_Engine\output\
3. Latest movie_*.mp4 file dekho
4. Double-click karo VLC/Media Player se kholne ke liye
```

Option C: **Browser Mein Video Player**
```
Add this route to web_app.py:

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(
        os.path.join(OUTPUT_FOLDER, filename),
        as_attachment=True
    )

Then access: http://localhost:5000/download/movie_1768690458.043417.mp4
```

### 5. **Current Status (Demo Mode)**

⚠️ **CURRENTLY**: System demo mode mein chal raha hai kyunki:
- ✅ Subtitles generate ho rahe hain (✓ Verified)
- ❌ Actual video files `.mp4` and `.wav` files create nahi ho rahe kyunki:
  - Blender integration needed
  - ffmpeg/MediaPipe dependencies missing
  - EmotionalVoiceEngine actual files create nahi kar pa raha

### 6. **Real Output Kaise Generate Hoga?**

#### **Option 1: Install All Dependencies**
```bash
pip install -r requirements.txt

# Specifically:
pip install opencv-python-headless
pip install torch torchvision
pip install moviepy
pip install imageio-ffmpeg
```

#### **Option 2: Use Blender Integration**
```python
from src.blender.vfx_processor import VFXProcessor

vfx = VFXProcessor()
output = vfx.process_video_with_vfx(
    input_path="raw_video.mp4",
    output_path="e:\\Srijan_Engine\\output\\movie_final.mp4",
    vfx_config={
        'color_grade': 'teal_orange',
        'grain': 0.05,
        'sharpness': 0.8
    }
)
```

#### **Option 3: Use Emotional Voice Engine Directly**
```python
from src.audio.emotional_voice_engine import EmotionalVoiceEngine

engine = EmotionalVoiceEngine()
audio_path = engine.generate_emotional_voice(
    text="Welcome to Saipooja Warehouse!",
    emotion="happy"
)
# Output saved to: e:\Srijan_Engine\output\narration_*.wav
```

### 7. **Test Command - Direct Video Generation**

```python
import subprocess
import os

output_dir = r"e:\Srijan_Engine\output"

# Create simple test video with ffmpeg
cmd = [
    'ffmpeg',
    '-f', 'lavfi',
    '-i', 'color=c=blue:s=1280x720:d=5',  # 5 second blue video
    '-i', 'narration.wav',  # Add narration
    '-c:v', 'libx264',
    '-c:a', 'aac',
    os.path.join(output_dir, 'test_video.mp4')
]

subprocess.run(cmd)
```

### 8. **Accessing Generated Files**

**Method 1: Via Python**
```python
from pathlib import Path

output_dir = Path(r"e:\Srijan_Engine\output")
videos = list(output_dir.glob("movie_*.mp4"))

for video in videos:
    print(f"Found: {video}")
    print(f"Size: {video.stat().st_size / 1024 / 1024:.2f} MB")
```

**Method 2: Via Flask Route**
```python
@app.route('/api/videos', methods=['GET'])
def list_videos():
    videos = os.listdir(OUTPUT_FOLDER)
    mp4_files = [f for f in videos if f.endswith('.mp4')]
    return jsonify({'videos': mp4_files})
```

**Method 3: Via Command Line**
```bash
# List all output files
dir e:\Srijan_Engine\output\

# Play latest video
e:\Srijan_Engine\output\movie_*.mp4
```

### 9. **Current Generated Files (✓ Verified)**

```
Total Files Generated: 5 Subtitle files

✅ subtitles_1768690301.892827.srt
✅ subtitles_1768690307.777353.srt
✅ subtitles_1768690310.247607.srt
✅ subtitles_1768690312.685572.srt
✅ subtitles_1768690458.044422.srt

📁 Location: e:\Srijan_Engine\output\
```

### 10. **Next Steps**

To get **full video + audio** generation working:

1. ✅ **Install ffmpeg** (for video encoding)
   ```bash
   # Already partially configured
   choco install ffmpeg  # If using Chocolatey
   ```

2. ✅ **Configure Blender** (for 3D rendering)
   ```bash
   # Set Blender path in web_app.py
   BLENDER_PATH = r"e:\Srijan_Engine\blender_portable\5.0\blender.exe"
   ```

3. ✅ **Enable Audio Generation** (for narration)
   ```bash
   pip install google-genai pyttsx3 gtts
   ```

4. ✅ **Enable Video Processing** (for effects)
   ```bash
   pip install opencv-python moviepy imageio-ffmpeg
   ```

---

## 🎬 Quick Summary

| What | Where | Status |
|------|-------|--------|
| **Subtitle Files** | `e:\Srijan_Engine\output\subtitles_*.srt` | ✅ Working |
| **Narration Audio** | `e:\Srijan_Engine\output\narration_*.wav` | ⏳ Demo mode |
| **Final Video** | `e:\Srijan_Engine\output\movie_*.mp4` | ⏳ Demo mode |
| **Web Browser** | `http://localhost:5000/downloads/` | 🔧 To add |
| **Video Player** | Windows Media Player / VLC | ✅ Ready to use |

---

## 🚀 To Enable Full Video Generation

Replace the `/api/generate-movie` endpoint implementation to actually call:
1. `EmotionalVoiceEngine.generate_emotional_voice()` → creates .wav
2. `VFXProcessor.process_video_with_vfx()` → creates .mp4 with effects
3. Combine audio + video using `moviepy` or `ffmpeg`

Currently it's in **demo/mock mode** showing what WOULD be generated.
