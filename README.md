# Srijan Engine

**Status: ✅ COMPLETE & PRODUCTION READY** ([See Completion Summary](COMPLETION_SUMMARY.md))

Advanced AI Text-to-Movie software that converts text scripts into 3D animated scenes with professional narration, subtitles, and visual effects.

## 🚀 Quick Start

### Web Interface (Recommended)
```bash
python web_app.py
# Open: http://localhost:5000
```

### Desktop App
```bash
python -m src.gui.main
```

### Test Pipeline
```bash
python test_complete_pipeline.py
```

## 📚 Documentation
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Get started in 5 minutes
- **[COMPLETE_USAGE_GUIDE.md](COMPLETE_USAGE_GUIDE.md)** - Full API documentation
- **[IMPLEMENTATION_DETAILS.md](IMPLEMENTATION_DETAILS.md)** - Technical details
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - All docs overview

## Tech Stack
- Python 3.8+
- Flask (Web API)
- CustomTkinter (Desktop GUI)
- Blender 5.0 (Portable, rendering)
- OpenCV, MoviePy (Video processing)
- Librosa, Pydub (Audio processing)

## Features
✅ AI Script Parsing → Automatic scene extraction  
✅ Emotional Voice Narration → 7 emotion presets  
✅ Professional Video Rendering → Blender integration  
✅ Visual Effects → Color grading, grain, vignette  
✅ Subtitle Generation → SRT format  
✅ Audio-Visual Synchronization → Complete merge  
✅ Web API → REST endpoints  
✅ Desktop GUI → Full-featured interface  
✅ Error Handling → Intelligent fallbacks  
✅ Test Suite → 6/6 passing  

## Setup
1. Ensure Python 3.8+ is installed
2. Install dependencies: `pip install -r requirements.txt`
3. Optional: Place Blender in `blender_portable/` folder
4. Run `python web_app.py` for web interface or `python -m src.gui.main` for desktop

## Usage
Enter a script and click "Generate Movie" to create a complete video with narration and effects.