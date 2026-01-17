import subprocess
import os
import tempfile
import uuid
import librosa
import numpy as np

def analyze_audio(audio_path):
    """
    Analyzes the audio file to get duration and RMS energy for lip-sync.
    """
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    rms = rms / np.max(rms) if np.max(rms) > 0 else rms
    return duration, rms

def generate_lip_sync_code(duration, rms, char_name=None):
    """
    Generates Blender Python code for lip-sync animation.
    """
    fps = 24
    frame_end = int(duration * fps)
    num_frames = len(rms)
    step = max(1, num_frames // frame_end)  # Sample rms every few frames

    if char_name and char_name != 'Basic Head':
        from .assets_manager import load_character
        char_code = load_character(char_name)
        head_creation = char_code
    else:
        head_creation = """
# Create a simple head model
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=(0, 0, 1.5))
head = bpy.context.active_object
head.name = 'Head'

# Add shape key for mouth
bpy.ops.object.shape_key_add(from_mix=False)
mouth_shape = head.data.shape_keys.key_blocks['Key 1']
mouth_shape.name = 'mouth_open'

# Modify shape key: deform vertices for open mouth (simple deformation)
for vert in head.data.vertices:
    if vert.co.z < 0:  # Lower part
        mouth_shape.data[vert.index].co = vert.co * 1.2  # Scale down
"""

    code = f"""
# Lip-Sync Setup
import bpy

# Set animation length
bpy.context.scene.frame_end = {frame_end}
bpy.context.scene.render.fps = {fps}

{head_creation}

# Add camera focusing on face
bpy.ops.object.camera_add(location=(0, -3, 1.5))
camera = bpy.context.active_object
camera.name = 'FaceCamera'
bpy.context.scene.camera = camera

# Point camera at head
constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = head
constraint.track_axis = 'TRACK_NEGATIVE_Z'

# Animate shape key based on audio RMS
rms_data = {rms.tolist()}
step = {step}
for frame in range(0, {frame_end}, 1):
    rms_index = min(frame * step, len(rms_data) - 1)
    value = rms_data[rms_index]
    mouth_shape.value = value
    mouth_shape.keyframe_insert(data_path='value', frame=frame)
"""
    return code

def render_scene(bpy_code, blender_path, audio_path=None, script=None, env_name=None, char_name=None):
    """
    Renders the scene using the provided bpy_code and Blender executable.
    Saves the output as a unique .mp4 file in the output/ folder.
    """
    mood = None
    duration = 10  # default
    if script:
        from .assets_manager import detect_mood, get_lighting_for_mood
        mood = detect_mood(script)
        lighting_code = get_lighting_for_mood(mood)
        bpy_code += "\n\n" + lighting_code

    if env_name:
        from .assets_manager import load_environment
        env_code = load_environment(env_name)
        bpy_code += "\n\n" + env_code

    if audio_path:
        duration, rms = analyze_audio(audio_path)
        lip_sync_code = generate_lip_sync_code(duration, rms, char_name)
        bpy_code += "\n\n" + lip_sync_code

    # Process effects
    from .effects_processor import process_effects
    bpy_code = process_effects(bpy_code, script or "", audio_path, mood, duration)

    # Save bpy_code to a temporary .py file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(bpy_code)
        temp_script = f.name

    # Prepare output path with unique name
    output_dir = "D:/Srijan_Engine/output"
    os.makedirs(output_dir, exist_ok=True)
    unique_name = str(uuid.uuid4()) + ".mp4"
    output_path = os.path.join(output_dir, unique_name)

    # Run portable Blender in background mode with Eevee engine and GPU for speed
    cmd = [
        blender_path,
        "--background",
        "--python", temp_script,
        "--render-output", output_path,
        "--render-format", "FFMPEG",
        "--render-ffmpeg-format", "MPEG4",
        "--render-ffmpeg-video-codec", "H264",
        "--render-ffmpeg-audio-codec", "AAC",
        "--render-engine", "BLENDER_EEVEE",
        "--render-device", "GPU"  # Optimized for speed on capable hardware
    ]
    subprocess.run(cmd)

    # Clean up temporary script
    os.unlink(temp_script)

    return output_path