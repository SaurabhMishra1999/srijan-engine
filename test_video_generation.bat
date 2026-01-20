@echo off
REM Srijan Engine - Video Generation Test Script
REM Simple test runner

echo.
echo ========================================
echo SRIJAN ENGINE - VIDEO GENERATION TEST
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version 2>nul || (
    echo ERROR: Python not found in PATH
    echo.
    echo Please ensure Python is installed and added to PATH
    echo Checking virtual environment...
    if exist .venv (
        echo Found virtual environment at .venv
        call .venv\Scripts\activate.bat
        python --version
    ) else (
        echo Creating virtual environment...
        python -m venv .venv
        call .venv\Scripts\activate.bat
    )
)

echo.
echo Running import tests...
python -c "from src.audio.emotional_voice_engine import EmotionalVoiceEngine; print('OK: EmotionalVoiceEngine')"
python -c "from src.audio.audio_visual_merger import AudioVisualMerger; print('OK: AudioVisualMerger')"
python -c "from src.blender.vfx_processor import VFXProcessor; print('OK: VFXProcessor')"
python -c "from src.blender.warehouse_assets_manager import WarehouseAssetsManager; print('OK: WarehouseAssetsManager')"

echo.
echo ========================================
echo QUICK TEST - Generate Emotional Voice
echo ========================================
echo.

python << 'EOF'
import sys
sys.path.insert(0, 'src')

try:
    from audio.emotional_voice_engine import EmotionalVoiceEngine
    import os
    
    print("[*] Initializing EmotionalVoiceEngine...")
    engine = EmotionalVoiceEngine()
    print("[OK] Engine initialized")
    
    print("[*] Generating happy voice...")
    audio = engine.generate_emotional_voice(
        "Welcome to Srijan Engine test",
        emotion="happy",
        filename="test_happy_voice.wav"
    )
    
    if os.path.exists(audio):
        size = os.path.getsize(audio) / 1024
        print(f"[OK] Voice generated: {audio} ({size:.1f} KB)")
    else:
        print(f"[ERROR] File not created")
        
except Exception as e:
    import traceback
    print(f"[ERROR] {e}")
    traceback.print_exc()
EOF

echo.
echo ========================================
echo QUICK TEST - Warehouse Assets
echo ========================================
echo.

python << 'EOF'
import sys
sys.path.insert(0, 'src')

try:
    from blender.warehouse_assets_manager import WarehouseAssetsManager
    
    print("[*] Initializing WarehouseAssetsManager...")
    manager = WarehouseAssetsManager()
    print("[OK] Manager initialized")
    
    print("[*] Getting asset statistics...")
    stats = manager.get_asset_statistics()
    print(f"[OK] Total assets: {stats['total_assets']}")
    for asset_type, count in stats['by_type'].items():
        print(f"     - {asset_type}: {count}")
    
    print("[*] Creating test warehouse scene...")
    scene = manager.create_scene(
        "Test Warehouse",
        "test_wh_001",
        "Test warehouse scene"
    )
    print(f"[OK] Scene created: {scene.scene_name}")
    
    print("[*] Adding forklift to scene...")
    manager.add_asset_to_scene("test_wh_001", "forklift_001", position=(0, 0, 0))
    print("[OK] Forklift added")
    
except Exception as e:
    import traceback
    print(f"[ERROR] {e}")
    traceback.print_exc()
EOF

echo.
echo ========================================
echo OUTPUT FILES
echo ========================================
echo.
echo Generated files in:
echo   - assets/audio/
echo   - output/
echo.
echo Run 'dir assets\audio' to see generated voice files
echo.
pause
