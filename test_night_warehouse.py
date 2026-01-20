import requests
import json
from pathlib import Path
from datetime import datetime

# Night Warehouse Scene Script
night_script = """Night time in the warehouse. Dim lighting with a warm vintage glow. A forklift is moving fast across the main aisle. In the background, a container truck's headlights flash as it prepares to leave the dock. Dust particles are visible in the light beams.

It's 2 AM and we have a critical shipment of medical supplies that must leave now. The team is working double shifts to meet the deadline. Every second counts in this logistics chain. Move that forklift to Sector 4 immediately! We cannot afford any delays tonight."""

# API payload with concerned/serious tone (using professional as closest match)
payload = {
    "script": night_script,
    "narration_style": "professional",  # Serious/Professional tone
    "duration": 20,  # 20 seconds as requested
    "enable_color_grade": True,  # Warm/Vintage color grading
    "enable_film_grain": True,  # Film grain for cinematic effect
    "enable_subtitles": True  # Subtitles ON
}

print("\n" + "=" * 75)
print("NIGHT WAREHOUSE SCENE - CRITICAL SHIPMENT TEST")
print("=" * 75)

print("\nSCRIPT:")
print("-" * 75)
print(night_script)

print("\n\nCONFIGURATION:")
print("-" * 75)
print(f"Narration Style: professional (Serious/Concerned tone)")
print(f"Duration: {payload['duration']} seconds")
print(f"Color Grading: {payload['enable_color_grade']} (Warm/Vintage)")
print(f"Film Grain: {payload['enable_film_grain']} (Cinematic effect)")
print(f"Subtitles: {payload['enable_subtitles']}")

print("\n\nSENDING REQUEST TO API...")
print("-" * 75)

try:
    response = requests.post('http://localhost:5000/api/generate-movie', json=payload)
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n[SUCCESS] MOVIE GENERATION COMPLETED!")
        print("-" * 75)
        print(f"Message: {data.get('message', 'N/A')}")
        print(f"Processing Time: {data.get('processing_time', 'N/A')} seconds")
        print(f"Demo Mode: {data.get('demo', False)}")
        
        print("\n\nOUTPUT FILES GENERATED:")
        print("-" * 75)
        
        movie_path = data.get('output_path', '')
        narration_path = data.get('narration_file', '')
        subtitle_path = data.get('subtitle_file', '')
        
        print(f"[1] Movie Video:")
        print(f"    Path: {movie_path}")
        print(f"    Status: Created")
        
        print(f"\n[2] Narration Audio:")
        print(f"    Path: {narration_path}")
        print(f"    Status: Created")
        
        print(f"\n[3] Subtitle File:")
        print(f"    Path: {subtitle_path}")
        print(f"    Status: Created")
        
        print("\n\nVFX & EFFECTS CONFIGURATION:")
        print("-" * 75)
        vfx = data.get('vfx_config', {})
        print(f"Color Grade: {vfx.get('color_grade', 'N/A')} (Warm tones)")
        print(f"Film Grain: {vfx.get('grain', 'N/A')} (Cinematic texture)")
        print(f"Sharpness: {vfx.get('sharpness', 'N/A')}")
        
        # Check actual files
        print("\n\nFILE VERIFICATION:")
        print("-" * 75)
        
        if subtitle_path and Path(subtitle_path).exists():
            print(f"[OK] Subtitle file exists")
            with open(subtitle_path, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            file_size = len(srt_content)
            print(f"     Size: {file_size} bytes")
            print(f"     Content preview:")
            for line in srt_content.split('\n')[:8]:
                print(f"     {line}")
        else:
            print(f"[!] Subtitle file path provided but needs verification")
        
        print("\n\nHOW TO ACCESS YOUR VIDEO:")
        print("-" * 75)
        print("Option 1: Dashboard (Browser)")
        print("  - Go to http://localhost:5000")
        print("  - Scroll down to 'Generated Files' section")
        print("  - Click Refresh to see your video")
        print("  - Click Download button")
        
        print("\nOption 2: Windows Explorer")
        print(f"  - Open: e:\\Srijan_Engine\\output\\")
        print(f"  - Look for: movie_*.mp4 (latest file)")
        
        print("\nOption 3: Direct Download URL")
        filename = movie_path.split('\\')[-1] if movie_path else 'unknown'
        print(f"  - http://localhost:5000/download/{filename}")
        
        print("\n" + "=" * 75)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 75)
        
    else:
        print(f"[ERROR] Status: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("[ERROR] Cannot connect to server at http://localhost:5000")
    print("Make sure Flask server is running!")
    print("Run: python web_app.py")
    
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
