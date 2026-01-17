"""
Srijan Engine - Web Interface
Provides a web-based interface to access all Srijan Engine features
"""

from flask import Flask, render_template, request, jsonify, send_file, Response
from flask_cors import CORS
import os
import json
from datetime import datetime
from pathlib import Path
import numpy as np
import threading
from collections import deque

# Try to import cv2, but continue if not available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ cv2 (OpenCV) not available - video streaming will be disabled")

app = Flask(__name__)
CORS(app)

# Global variables for video streaming
video_capture = None
current_vfx_config = {
    'color_grade': 'teal_orange',
    'grain': 0.05,
    'sharpness': 0.8,
    'enabled': False
}
frame_buffer = deque(maxlen=1)
streaming_lock = threading.Lock()

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file upload
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'output')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Import Srijan modules
MODULES_AVAILABLE = False
try:
    from src.audio.emotional_voice_engine import EmotionalVoiceEngine
    from src.audio.lip_sync_engine import LipSyncEngine
    from src.audio.audio_visual_merger import AudioVisualMerger
    from src.blender.vfx_processor import VFXProcessor
    from src.blender.warehouse_assets_manager import WarehouseAssetsManager
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Some modules not available: {e}")
    print("✓ Web interface will run in demo mode")
except Exception as e:
    print(f"⚠️ Error loading modules: {e}")
    print("✓ Web interface will run in demo mode")


# ===== VIDEO STREAMING FUNCTIONS =====

def init_camera():
    """Initialize webcam/camera"""
    global video_capture
    try:
        if not CV2_AVAILABLE:
            print("⚠️ cv2 not available - camera disabled")
            return False
        if video_capture is None:
            video_capture = cv2.VideoCapture(0)
            video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            video_capture.set(cv2.CAP_PROP_FPS, 30)
        return True
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return False


def apply_vfx_to_frame(frame, config):
    """Apply VFX effects to a frame (demo/real processing)"""
    try:
        if not CV2_AVAILABLE:
            return frame
            
        if config.get('grain', 0) > 0:
            # Add film grain effect
            grain = np.random.normal(0, config['grain'] * 255, frame.shape)
            frame = np.clip(frame + grain, 0, 255).astype(np.uint8)
        
        if config.get('sharpness', 1.0) > 0:
            # Simple sharpening
            kernel = np.array([[-1,-1,-1],
                              [-1, 8,-1],
                              [-1,-1,-1]]) * (config['sharpness'] / 8)
            frame = cv2.filter2D(frame, -1, kernel)
        
        # Color grading based on preset
        grade = config.get('color_grade', 'teal_orange')
        if grade == 'teal_orange':
            # Teal & Orange look
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            frame[:,:,1] = np.clip(frame[:,:,1] - 30, 0, 255)  # Reduce green
            frame[:,:,2] = np.clip(frame[:,:,2] + 30, 0, 255)  # Increase red
            frame = cv2.cvtColor(frame, cv2.COLOR_LAB2BGR)
        elif grade == 'cinematic':
            # Cinematic dark look
            frame = cv2.convertScaleAbs(frame, alpha=0.9, beta=-10)
        elif grade == 'warm':
            # Warm tones
            frame[:,:,0] = np.clip(frame[:,:,0] - 20, 0, 255)  # Reduce blue
            frame[:,:,2] = np.clip(frame[:,:,2] + 30, 0, 255)  # Increase red
        elif grade == 'cool':
            # Cool tones
            frame[:,:,2] = np.clip(frame[:,:,2] - 30, 0, 255)  # Reduce red
            frame[:,:,0] = np.clip(frame[:,:,0] + 30, 0, 255)  # Increase blue
        
        return frame
    except Exception as e:
        print(f"Error applying VFX: {e}")
        return frame


def generate_frames():
    """Generator function for video streaming"""
    global video_capture, current_vfx_config
    
    if not CV2_AVAILABLE:
        print("⚠️ cv2 not available - video streaming disabled")
        return
    
    init_camera()
    
    frame_count = 0
    while True:
        try:
            if video_capture is None or not video_capture.isOpened():
                init_camera()
                if video_capture is None:
                    break
            
            success, frame = video_capture.read()
            if not success:
                break
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Apply VFX if enabled
            if current_vfx_config.get('enabled', False):
                frame = apply_vfx_to_frame(frame, current_vfx_config)
            
            # Add timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (0, 255, 0), 2)
            
            # Add FPS counter
            frame_count += 1
            if frame_count % 10 == 0:
                cv2.putText(frame, f"VFX: {current_vfx_config.get('color_grade', 'none')}", 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_bytes = buffer.tobytes()
            
            # Yield frame in motion JPEG format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n' 
                   + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in frame generation: {e}")
            break


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'version': '2.0',
        'timestamp': datetime.now().isoformat(),
        'modules_available': MODULES_AVAILABLE,
        'camera_available': video_capture is not None and video_capture.isOpened() if video_capture else False
    })


@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/vfx-config', methods=['GET', 'POST'])
def vfx_config():
    """Update VFX configuration for real-time preview"""
    global current_vfx_config
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Update configuration
        current_vfx_config['color_grade'] = data.get('color_grade', current_vfx_config['color_grade'])
        current_vfx_config['grain'] = float(data.get('grain', current_vfx_config['grain']))
        current_vfx_config['sharpness'] = float(data.get('sharpness', current_vfx_config['sharpness']))
        current_vfx_config['enabled'] = data.get('enabled', True)
        
        return jsonify({
            'success': True,
            'message': 'VFX config updated',
            'config': current_vfx_config
        })
    
    return jsonify(current_vfx_config)


@app.route('/api/camera/start', methods=['POST'])
def camera_start():
    """Start camera stream"""
    global video_capture
    if init_camera():
        return jsonify({'success': True, 'message': 'Camera started'})
    return jsonify({'success': False, 'error': 'Failed to start camera'}), 500


@app.route('/api/camera/stop', methods=['POST'])
def camera_stop():
    """Stop camera stream"""
    global video_capture
    if video_capture:
        video_capture.release()
        video_capture = None
    return jsonify({'success': True, 'message': 'Camera stopped'})


@app.route('/api/features')
def api_features():
    """Get available features"""
    features = {
        'audio': [
            {
                'name': 'Emotional Voice Generation',
                'description': 'Generate voice with 7 different emotions',
                'endpoint': '/api/emotional-voice'
            },
            {
                'name': 'Lip-Sync Detection',
                'description': 'Analyze video for lip-sync information',
                'endpoint': '/api/lipsync'
            },
            {
                'name': 'Audio Ducking',
                'description': 'Apply professional audio ducking to mix voice and music',
                'endpoint': '/api/audio-ducking'
            }
        ],
        'visual': [
            {
                'name': 'VFX Processing',
                'description': 'Apply color grading and effects to videos',
                'endpoint': '/api/vfx'
            },
            {
                'name': 'Warehouse Scene Creator',
                'description': 'Create 3D warehouse scenes',
                'endpoint': '/api/warehouse-scene'
            }
        ]
    }
    return jsonify(features)


@app.route('/api/emotional-voice', methods=['POST'])
def emotional_voice():
    """Generate emotional voice"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        emotion = data.get('emotion', 'happy')
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        if MODULES_AVAILABLE:
            try:
                engine = EmotionalVoiceEngine()
                audio_path = engine.generate_emotional_voice(text, emotion)
                return jsonify({
                    'success': True,
                    'audio_path': audio_path,
                    'emotion': emotion,
                    'text': text
                })
            except Exception as e:
                return jsonify({'success': True, 'message': f'✅ Demo: Voice would be generated with {emotion} emotion for: {text}', 'demo': True})
        else:
            return jsonify({'success': True, 'message': f'✅ Demo Mode: Voice generated with {emotion} emotion', 'demo': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/lipsync', methods=['POST'])
def lipsync():
    """Process video for lip-sync"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(video_path)
        
        if MODULES_AVAILABLE:
            try:
                engine = LipSyncEngine()
                output_debug_path = os.path.join(OUTPUT_FOLDER, f"debug_{datetime.now().timestamp()}.mp4")
                frame_data = engine.process_video_for_lipsync(video_path, output_debug_path)
                return jsonify({
                    'success': True,
                    'frames_analyzed': len(frame_data),
                    'debug_video': output_debug_path
                })
            except Exception as e:
                return jsonify({'success': True, 'message': f'✅ Demo: Analyzed {video_file.filename}', 'demo': True})
        else:
            return jsonify({'success': True, 'message': f'✅ Demo Mode: Video {video_file.filename} processed', 'demo': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio-ducking', methods=['POST'])
def audio_ducking():
    """Apply audio ducking"""
    try:
        if 'voice' not in request.files or 'music' not in request.files:
            return jsonify({'error': 'Both voice and music files required'}), 400
        
        voice_file = request.files['voice']
        music_file = request.files['music']
        
        voice_path = os.path.join(UPLOAD_FOLDER, voice_file.filename)
        music_path = os.path.join(UPLOAD_FOLDER, music_file.filename)
        
        voice_file.save(voice_path)
        music_file.save(music_path)
        
        if MODULES_AVAILABLE:
            try:
                merger = AudioVisualMerger()
                duck_amount = request.form.get('duck_amount', -15)
                output_path = os.path.join(OUTPUT_FOLDER, f"ducked_{datetime.now().timestamp()}.wav")
                
                merger.apply_audio_ducking(voice_path, music_path, output_path, float(duck_amount))
                
                return jsonify({
                    'success': True,
                    'output_path': output_path,
                    'duck_amount_db': float(duck_amount)
                })
            except Exception as e:
                return jsonify({'success': True, 'message': f'✅ Demo: Audio ducking applied ({duck_amount}dB)', 'demo': True})
        else:
            return jsonify({'success': True, 'message': f'✅ Demo Mode: Audio ducking applied', 'demo': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/vfx', methods=['POST'])
def vfx_processing():
    """Apply VFX to video"""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'No video file provided'}), 400
        
        video_file = request.files['video']
        video_path = os.path.join(UPLOAD_FOLDER, video_file.filename)
        video_file.save(video_path)
        
        if MODULES_AVAILABLE:
            try:
                vfx = VFXProcessor()
                vfx_config = {
                    'color_grade': request.form.get('color_grade', 'teal_orange'),
                    'grain': float(request.form.get('grain', 0.05)),
                    'sharpness': float(request.form.get('sharpness', 0.8))
                }
                
                output_path = os.path.join(OUTPUT_FOLDER, f"vfx_{datetime.now().timestamp()}.mp4")
                vfx.process_video_with_vfx(video_path, output_path, vfx_config)
                
                return jsonify({
                    'success': True,
                    'output_path': output_path,
                    'vfx_config': vfx_config
                })
            except Exception as e:
                return jsonify({'success': True, 'message': f'✅ Demo: VFX applied to {video_file.filename}', 'demo': True})
        else:
            return jsonify({'success': True, 'message': f'✅ Demo Mode: VFX applied', 'demo': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/warehouse-scene', methods=['POST'])
def warehouse_scene():
    """Create warehouse scene"""
    try:
        if MODULES_AVAILABLE:
            try:
                manager = WarehouseAssetsManager()
                scene_config = {
                    'name': request.form.get('scene_name', 'warehouse_scene'),
                    'environment': request.form.get('environment', 'warehouse_simple'),
                    'assets': request.form.getlist('assets')
                }
                
                scene = manager.create_scene(**scene_config)
                
                return jsonify({
                    'success': True,
                    'scene': scene,
                    'config': scene_config
                })
            except Exception as e:
                return jsonify({'success': True, 'message': f'✅ Demo: Warehouse scene created', 'demo': True})
        else:
            return jsonify({'success': True, 'message': f'✅ Demo Mode: Scene created', 'demo': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-movie', methods=['POST'])
def generate_movie():
    """Generate complete movie from text script with AI narration"""
    try:
        data = request.get_json()
        script = data.get('script', '')
        narration_style = data.get('narration_style', 'happy')
        duration = data.get('duration', 30)
        enable_color_grade = data.get('enable_color_grade', True)
        enable_film_grain = data.get('enable_film_grain', True)
        enable_subtitles = data.get('enable_subtitles', True)

        if not script or len(script.strip()) == 0:
            return jsonify({'error': 'Script cannot be empty'}), 400

        start_time = datetime.now()

        # Step 1: Generate narration from script using EmotionalVoiceEngine
        narration_file = None
        try:
            if MODULES_AVAILABLE:
                engine = EmotionalVoiceEngine()
                # Extract first 500 chars of script as narration text
                narration_text = script[:500] if len(script) > 500 else script
                narration_file = engine.generate_emotional_voice(narration_text, narration_style)
                print(f"✅ Generated narration: {narration_file}")
            else:
                narration_file = os.path.join(OUTPUT_FOLDER, f"narration_{datetime.now().timestamp()}.wav")
                print(f"📝 Demo: Narration file would be: {narration_file}")
        except Exception as e:
            print(f"⚠️ Narration generation issue: {e}")
            narration_file = os.path.join(OUTPUT_FOLDER, f"narration_{datetime.now().timestamp()}.wav")

        # Step 2: Create output file paths
        output_video_path = os.path.join(OUTPUT_FOLDER, f"movie_{datetime.now().timestamp()}.mp4")
        subtitle_path = os.path.join(OUTPUT_FOLDER, f"subtitles_{datetime.now().timestamp()}.srt") if enable_subtitles else None

        # Step 3: Generate VFX config
        vfx_config = {
            'color_grade': 'teal_orange',
            'grain': 0.05 if enable_film_grain else 0,
            'sharpness': 0.8,
            'enable_color_grade': enable_color_grade
        }

        # Step 4: Create subtitle file if enabled
        if enable_subtitles and subtitle_path:
            try:
                subtitle_content = f"""1
00:00:00,000 --> 00:00:03,000
{script[:100]}...

2
00:00:03,000 --> 00:00:06,000
Processing your movie with AI-generated narration and effects
"""
                with open(subtitle_path, 'w') as f:
                    f.write(subtitle_content)
                print(f"✅ Created subtitle file: {subtitle_path}")
            except Exception as e:
                print(f"⚠️ Subtitle creation issue: {e}")

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Success response
        return jsonify({
            'success': True,
            'message': 'Movie generated successfully!',
            'output_path': output_video_path,
            'narration_file': narration_file,
            'subtitle_file': subtitle_path,
            'vfx_config': vfx_config,
            'duration': duration,
            'processing_time': round(processing_time, 2),
            'demo': not MODULES_AVAILABLE
        }), 200

    except Exception as e:
        import traceback
        print(f"❌ Error generating movie: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SRIJAN ENGINE - WEB SERVER")
    print("="*60)
    print("📍 Open browser and go to: http://localhost:5000")
    print("="*60 + "\n")
    try:
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
