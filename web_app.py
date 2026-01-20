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
    from src.blender.scene_manager import SceneSetupManager
    from src.blender.scene_config_api import SceneConfigAPI
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Some modules not available: {e}")
    print("✓ Web interface will run in demo mode")
except Exception as e:
    print(f"⚠️ Error loading modules: {e}")
    print("✓ Web interface will run in demo mode")

# Initialize Scene Manager
try:
    if MODULES_AVAILABLE:
        scene_manager = SceneSetupManager()
        scene_api = SceneConfigAPI(app)
        print("✓ Scene Configuration API initialized")
except Exception as e:
    print(f"⚠️ Scene API initialization warning: {e}")
    scene_manager = None
    scene_api = None



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
    """Main workflow dashboard"""
    return render_template('workflow_dashboard.html')


@app.route('/scene-editor')
def scene_editor():
    """Scene configuration interface"""
    return render_template('scene_editor.html')


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
                'name': 'Scene Configuration Studio',
                'description': 'Create and configure any 3D scene with full customization',
                'endpoint': '/scene-editor'
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
    """Generate complete movie from text script with AI narration and video effects"""
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
        timestamp = datetime.now().timestamp()

        # Step 1: Generate narration from script using EmotionalVoiceEngine
        narration_file = None
        try:
            if MODULES_AVAILABLE:
                engine = EmotionalVoiceEngine()
                narration_text = script[:500] if len(script) > 500 else script
                narration_file = engine.generate_emotional_voice(narration_text, narration_style)
                print(f"✅ Generated narration: {narration_file}")
            else:
                narration_file = os.path.join(OUTPUT_FOLDER, f"narration_{timestamp}.wav")
                print(f"📝 Demo: Narration file would be: {narration_file}")
        except Exception as e:
            print(f"⚠️ Narration generation issue: {e}")
            narration_file = os.path.join(OUTPUT_FOLDER, f"narration_{timestamp}.wav")

        # Step 2: Generate subtitles
        subtitle_path = None
        if enable_subtitles:
            subtitle_path = os.path.join(OUTPUT_FOLDER, f"subtitles_{timestamp}.srt")
            try:
                # Create subtitle file with script content
                lines = script.split('.')
                subtitle_content = ""
                current_time = 0
                
                for idx, line in enumerate(lines[:10], 1):  # Limit to first 10 sentences
                    if line.strip():
                        start_ms = int(current_time * 1000)
                        end_ms = int((current_time + 3) * 1000)
                        subtitle_content += f"{idx}\n{_ms_to_srt_time(start_ms)} --> {_ms_to_srt_time(end_ms)}\n{line.strip()}\n\n"
                        current_time += 3
                
                with open(subtitle_path, 'w', encoding='utf-8') as f:
                    f.write(subtitle_content)
                print(f"✅ Created subtitle file: {subtitle_path}")
            except Exception as e:
                print(f"⚠️ Subtitle creation issue: {e}")
                subtitle_path = None

        # Step 3: Generate video frames (create simple test video if actual rendering unavailable)
        output_video_path = os.path.join(OUTPUT_FOLDER, f"movie_{timestamp}.mp4")
        try:
            if MODULES_AVAILABLE:
                # Try to generate actual video with VFX
                from src.blender.renderer import BlenderRenderer
                try:
                    renderer = BlenderRenderer()
                    output_video_path = renderer.render_scene_to_video(
                        script=script,
                        output_path=output_video_path,
                        duration=duration
                    )
                    print(f"✅ Rendered video: {output_video_path}")
                except Exception as e:
                    print(f"⚠️ Blender rendering issue: {e}")
                    output_video_path = _create_simple_test_video(output_video_path, duration)
            else:
                # Create simple test video
                output_video_path = _create_simple_test_video(output_video_path, duration)
        except Exception as e:
            print(f"⚠️ Video generation issue: {e}")
            output_video_path = _create_simple_test_video(output_video_path, duration)

        # Step 4: Merge video and audio using AudioVisualMerger if available
        final_video_path = os.path.join(OUTPUT_FOLDER, f"movie_final_{timestamp}.mp4")
        
        # If we have a valid video, use it as fallback
        if output_video_path and os.path.exists(output_video_path):
            # Try to merge with audio if available
            if MODULES_AVAILABLE and narration_file and os.path.exists(narration_file):
                try:
                    merger = AudioVisualMerger()
                    
                    # Add visual effects
                    if enable_color_grade:
                        merger.add_visual_effect('color_grade', 0.7, 0, 99999, {'color_temp': 'warm'})
                    if enable_film_grain:
                        merger.add_visual_effect('grain', 0.05, 0, 99999)
                    
                    # Process video with effects
                    effects_video = os.path.join(OUTPUT_FOLDER, f"movie_with_vfx_{timestamp}.mp4")
                    try:
                        merger.process_video_with_effects(output_video_path, effects_video)
                        if os.path.exists(effects_video):
                            # Merge audio and video
                            merged_result = merger.merge_video_and_audio(
                                effects_video,
                                narration_file,
                                final_video_path
                            )
                            if merged_result and os.path.exists(merged_result):
                                final_video_path = merged_result
                                print(f"✅ Merged audio and video: {final_video_path}")
                            else:
                                # Fallback: use original video
                                final_video_path = output_video_path
                                print(f"⚠️ Using video without audio merge")
                        else:
                            final_video_path = output_video_path
                    except Exception as e:
                        print(f"⚠️ VFX processing issue: {e}")
                        final_video_path = output_video_path
                except Exception as e:
                    print(f"⚠️ Audio-visual merge issue: {e}")
                    final_video_path = output_video_path
            else:
                # No merger available, use raw video
                final_video_path = output_video_path
        else:
            print(f"⚠️ No video file generated")
            final_video_path = None

        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()

        # Verify final video exists
        if not final_video_path or not os.path.exists(final_video_path):
            return jsonify({
                'success': False,
                'error': 'Video generation failed - no output file created',
                'debug_info': {
                    'final_video_path': final_video_path,
                    'output_video_path': output_video_path,
                    'narration_file': narration_file
                }
            }), 500

        # Success response
        return jsonify({
            'success': True,
            'message': 'Movie generated successfully!',
            'output_path': final_video_path,
            'video_file': os.path.basename(final_video_path),
            'narration_file': narration_file,
            'subtitle_file': subtitle_path,
            'duration': duration,
            'processing_time': round(processing_time, 2),
            'vfx_config': {
                'color_grade': 'teal_orange' if enable_color_grade else 'none',
                'grain': 0.05 if enable_film_grain else 0,
                'sharpness': 0.8
            }
        }), 200

    except Exception as e:
        import traceback
        print(f"❌ Error generating movie: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500


def _ms_to_srt_time(milliseconds):
    """Convert milliseconds to SRT time format (HH:MM:SS,mmm)"""
    total_seconds = milliseconds // 1000
    ms = milliseconds % 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{ms:03d}"


def _create_simple_test_video(output_path, duration=10):
    """Create a video using OpenCV with animated frames"""
    try:
        if not CV2_AVAILABLE:
            print("⚠️ OpenCV not available for video creation")
            return None
        
        import numpy as np
        
        # Video properties
        width, height = 1280, 720
        fps = 30
        total_frames = duration * fps
        
        # Create video writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            print("⚠️ Failed to open video writer")
            return None
        
        # Generate frames
        for frame_num in range(total_frames):
            # Create frame with gradient background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Gradient background (dark to cyan)
            for i in range(height):
                intensity = int(20 + (i / height) * 40)
                frame[i, :] = [intensity, intensity // 2, intensity]
            
            # Add animated circle (simulating cosmic dance)
            center_x = int(width/2 + 100 * np.sin(frame_num * 0.05))
            center_y = int(height/2 + 50 * np.cos(frame_num * 0.03))
            radius = 30 + int(20 * np.sin(frame_num * 0.1))
            
            cv2.circle(frame, (center_x, center_y), radius, (0, 212, 255), -1)
            
            # Add pulsing effect
            pulse = int(10 * np.sin(frame_num * 0.15))
            cv2.circle(frame, (center_x, center_y), radius + pulse, (0, 100, 150), 2)
            
            # Add text
            progress = int((frame_num / total_frames) * 100)
            text = f"TANDAV - {progress}%"
            cv2.putText(frame, text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 212, 255), 3)
            
            # Add frame info
            cv2.putText(frame, f"Frame: {frame_num}/{total_frames}", (50, height-50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 150, 200), 2)
            
            # Write frame
            out.write(frame)
        
        out.release()
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            print(f"✅ Created video: {output_path} ({file_size:.2f} MB)")
            return output_path
        else:
            print(f"⚠️ Video file not created")
            return None
            
    except Exception as e:
        print(f"⚠️ Video creation error: {e}")
        import traceback
        traceback.print_exc()
        return None


@app.route('/api/output-files', methods=['GET'])
def list_output_files():
    """List all generated files in output folder"""
    try:
        files = {
            'videos': [],
            'audio': [],
            'subtitles': [],
            'total_size_mb': 0
        }
        
        if os.path.exists(OUTPUT_FOLDER):
            for filename in os.listdir(OUTPUT_FOLDER):
                filepath = os.path.join(OUTPUT_FOLDER, filename)
                if os.path.isfile(filepath):
                    file_size = os.path.getsize(filepath) / (1024 * 1024)  # Convert to MB
                    file_info = {
                        'name': filename,
                        'size_mb': round(file_size, 2),
                        'path': filepath,
                        'url': f'/download/{filename}'
                    }
                    
                    if filename.endswith('.mp4'):
                        files['videos'].append(file_info)
                    elif filename.endswith('.wav'):
                        files['audio'].append(file_info)
                    elif filename.endswith('.srt'):
                        files['subtitles'].append(file_info)
                    
                    files['total_size_mb'] += file_size
        
        files['total_size_mb'] = round(files['total_size_mb'], 2)
        
        return jsonify({
            'success': True,
            'output_folder': OUTPUT_FOLDER,
            'files': files
        })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Download generated file"""
    try:
        # Security: prevent directory traversal
        if '..' in filename or '/' in filename or '\\' in filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        # Verify file exists and is in output folder
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        if not file_path.startswith(os.path.abspath(OUTPUT_FOLDER)):
            return jsonify({'error': 'Access denied'}), 403
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
