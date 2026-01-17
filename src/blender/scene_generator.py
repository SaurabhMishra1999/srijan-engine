import subprocess
import os
import tempfile
import uuid
import librosa
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

def generate_armature_code(motion_capture_path, duration):
    """
    Generates bpy code to create armature and apply motion capture poses.
    """
    code = f"""
# Motion Capture Armature
import bpy
import json

# Load motion data
with open('{motion_capture_path}', 'r') as f:
    data = json.load(f)
frames = data['frames']
fps = data.get('fps', 30)

# Create simple armature
bpy.ops.object.armature_add(location=(0, 0, 0))
armature = bpy.context.active_object
armature.name = 'MotionArmature'

bpy.ops.object.mode_set(mode='EDIT')
bones = armature.data.edit_bones

# Define bones (simplified)
hips = bones.new('Hips')
hips.head = (0, 0, 0.8)
hips.tail = (0, 0, 1.0)

spine = bones.new('Spine')
spine.head = (0, 0, 1.0)
spine.tail = (0, 0, 1.3)

left_shoulder = bones.new('LeftShoulder')
left_shoulder.head = (-0.2, 0, 1.3)
left_shoulder.tail = (-0.4, 0, 1.3)

right_shoulder = bones.new('RightShoulder')
right_shoulder.head = (0.2, 0, 1.3)
right_shoulder.tail = (0.4, 0, 1.3)

# Parent bones
spine.parent = hips
left_shoulder.parent = spine
right_shoulder.parent = spine

bpy.ops.object.mode_set(mode='OBJECT')

# Parent head to spine
head = bpy.data.objects.get('Head')
if head:
    head.parent = armature
    head.parent_type = 'BONE'
    head.parent_bone = 'Spine'

# Apply motion
bpy.ops.object.mode_set(mode='POSE')
pose_bones = armature.pose.bones

scene_fps = 24
motion_frames = len(frames)
duration_frames = int({duration} * scene_fps)

for i in range(duration_frames):
    frame_num = i + 1
    bpy.context.scene.frame_set(frame_num)
    
    # Loop motion if shorter
    motion_idx = i % motion_frames
    frame_data = frames[motion_idx]
    
    # Simplified pose mapping (scale normalized coords)
    scale = 2.0  # Adjust scale
    if len(frame_data) > 23:  # MediaPipe has 33
        # Hips from left_hip (23) and right_hip (24)
        left_hip = frame_data[23]
        right_hip = frame_data[24]
        hips_x = (left_hip[0] + right_hip[0]) / 2 * scale - scale/2
        hips_y = (left_hip[1] + right_hip[1]) / 2 * scale - scale/2
        hips_z = (left_hip[2] + right_hip[2]) / 2 * scale
        pose_bones['Hips'].location = (hips_x, hips_y, hips_z)
        pose_bones['Hips'].keyframe_insert(data_path='location', frame=frame_num)
        
        # Shoulders
        if len(frame_data) > 11:
            left_shoulder_lm = frame_data[11]  # left_shoulder
            right_shoulder_lm = frame_data[12]  # right_shoulder
            pose_bones['LeftShoulder'].location = ((left_shoulder_lm[0] - 0.5) * scale, (left_shoulder_lm[1] - 0.5) * scale, (left_shoulder_lm[2]) * scale)
            pose_bones['RightShoulder'].location = ((right_shoulder_lm[0] - 0.5) * scale, (right_shoulder_lm[1] - 0.5) * scale, (right_shoulder_lm[2]) * scale)
            pose_bones['LeftShoulder'].keyframe_insert(data_path='location', frame=frame_num)
            pose_bones['RightShoulder'].keyframe_insert(data_path='location', frame=frame_num)

bpy.ops.object.mode_set(mode='OBJECT')
"""
    return code

def analyze_audio(audio_path):
    """
    Analyzes the audio file to get duration, RMS energy, and intensity for lip-sync.
    """
    y, sr = librosa.load(audio_path)
    duration = librosa.get_duration(y=y, sr=sr)
    rms = librosa.feature.rms(y=y)[0]
    rms = rms / np.max(rms) if np.max(rms) > 0 else rms
    # Extract intensity as average RMS
    intensity = np.mean(rms)
    return duration, rms, intensity

def generate_lip_sync_code(duration, rms, char_name=None, mood=None, intensity=1.0):
    """
    Generates Blender Python code for lip-sync animation and expressions.
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

# Add eyes
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(-0.15, 0.4, 1.6))
left_eye = bpy.context.active_object
left_eye.name = 'LeftEye'
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(0.15, 0.4, 1.6))
right_eye = bpy.context.active_object
right_eye.name = 'RightEye'

# Parent eyes to head
left_eye.parent = head
right_eye.parent = head

# Add shape key for mouth
bpy.ops.object.shape_key_add(from_mix=False)
mouth_shape = head.data.shape_keys.key_blocks['Key 1']
mouth_shape.name = 'mouth_open'

# Modify shape key: deform vertices for open mouth (simple deformation)
for vert in head.data.vertices:
    if vert.co.z < 0:  # Lower part
        mouth_shape.data[vert.index].co = vert.co * 1.2  # Scale down

# Add shape key for eye blink (scale eyes down)
bpy.ops.object.shape_key_add(from_mix=False)
blink_shape = head.data.shape_keys.key_blocks['Key 2']
blink_shape.name = 'eye_blink'

# Add mood-based shape keys
bpy.ops.object.shape_key_add(from_mix=False)
peaceful_shape = head.data.shape_keys.key_blocks['Key 3']
peaceful_shape.name = 'peaceful'
# Slight smile: lift mouth corners
for vert in head.data.vertices:
    if vert.co.z < 0 and abs(vert.co.x) > 0.1:
        peaceful_shape.data[vert.index].co = vert.co + (0, 0, 0.05)

bpy.ops.object.shape_key_add(from_mix=False)
angry_shape = head.data.shape_keys.key_blocks['Key 4']
angry_shape.name = 'angry'
# Lowered brows: deform upper forehead down
for vert in head.data.vertices:
    if vert.co.z > 0.3 and vert.co.y > 0:
        angry_shape.data[vert.index].co = vert.co + (0, 0, -0.1)

bpy.ops.object.shape_key_add(from_mix=False)
divine_shape = head.data.shape_keys.key_blocks['Key 5']
divine_shape.name = 'divine'
# Wide eyes: scale eyes up
for obj in [left_eye, right_eye]:
    for vert in obj.data.vertices:
        divine_shape.data[vert.index].co = vert.co * 1.2

# Set mood expression
if mood in ['Neutral', 'Bright']:
    peaceful_shape.value = 1
elif mood in ['Dark', 'Intense']:
    angry_shape.value = 1
elif mood == 'Divine':
    divine_shape.value = 1
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
intensity_factor = {intensity}
for frame in range(0, {frame_end}, 1):
    rms_index = min(frame * step, len(rms_data) - 1)
    value = rms_data[rms_index] * intensity_factor
    mouth_shape.value = value
    mouth_shape.keyframe_insert(data_path='value', frame=frame)

# Eye blinking animation
import random
random.seed(42)
blink_times = []
current_time = 0
fps = {fps}
while current_time < {frame_end} / fps:
    blink_times.append(int(current_time * fps))
    interval = random.uniform(3, 5)
    current_time += interval
for blink_frame in blink_times:
    if blink_frame + 3 < {frame_end}:
        blink_shape.value = 1
        blink_shape.keyframe_insert(data_path='value', frame=blink_frame)
        blink_shape.keyframe_insert(data_path='value', frame=blink_frame + 1)
        blink_shape.value = 0
        blink_shape.keyframe_insert(data_path='value', frame=blink_frame + 2)
"""
    return code

def render_scene(bpy_code, blender_path, audio_path=None, script=None, env_name=None, char_name=None, motion_capture_path=None, enable_bgm=False, voice_volume=1.0, bgm_volume=0.3):
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
        duration, rms, intensity = analyze_audio(audio_path)
        lip_sync_code = generate_lip_sync_code(duration, rms, char_name, mood, intensity)
        bpy_code += "\n\n" + lip_sync_code

    # Process effects
    from .effects_processor import process_effects
    bpy_code = process_effects(bpy_code, script or "", audio_path, mood, duration, enable_bgm, voice_volume, bgm_volume)

    if motion_capture_path:
        armature_code = generate_armature_code(motion_capture_path, duration)
        bpy_code += "\n\n" + armature_code

    # Save bpy_code to a temporary .py file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(bpy_code)
        temp_script = f.name

    # Prepare output path with unique name
    output_dir = os.path.join(BASE_DIR, 'output')
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

    # Auto-open output folder
    os.startfile(output_dir)

    # Clean up temporary script
    os.unlink(temp_script)

    return output_path

def preview_scene(bpy_code, blender_path, audio_path=None, script=None, env_name=None, char_name=None, motion_capture_path=None, enable_bgm=False, voice_volume=1.0, bgm_volume=0.3):
    """
    Renders a quick screenshot of the scene for preview.
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
        duration, rms, intensity = analyze_audio(audio_path)
        lip_sync_code = generate_lip_sync_code(duration, rms, char_name, mood, intensity)
        bpy_code += "\n\n" + lip_sync_code

    # Process effects
    from .effects_processor import process_effects
    bpy_code = process_effects(bpy_code, script or "", audio_path, mood, duration, enable_bgm, voice_volume, bgm_volume)

    if motion_capture_path:
        armature_code = generate_armature_code(motion_capture_path, duration)
        bpy_code += "\n\n" + armature_code

    # Create temp screenshot path
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        screenshot_path = f.name

    # Add screenshot code
    fps = 24
    frame_middle = int(duration * fps / 2)
    bpy_code += f"""
# Set to middle frame
bpy.context.scene.frame_set({frame_middle})

# Set low resolution for preview
bpy.context.scene.render.resolution_x = 854
bpy.context.scene.render.resolution_y = 480
bpy.context.scene.render.resolution_percentage = 100

# Screenshot filepath
bpy.context.scene.render.filepath = '{screenshot_path}'

# Render OpenGL screenshot
bpy.ops.render.opengl(write_still=True)
"""

    # Run portable Blender in background mode for screenshot
    cmd = [
        blender_path,
        "--background",
        "--python", temp_script,
    ]
    subprocess.run(cmd)

    # Clean up temporary script
    os.unlink(temp_script)

    return screenshot_path

def compile_videos(video_paths, blender_path):
    """
    Compiles multiple videos into one with transitions using Blender's Video Sequencer.
    """
    bpy_code = f"""
import bpy

# Set up video editing scene
bpy.context.scene.frame_end = 0

# Clear existing strips
for strip in bpy.context.scene.sequence_editor.sequences:
    bpy.context.scene.sequence_editor.sequences.remove(strip)

# Add videos with fade transitions
start_frame = 0
fade_duration = 24  # 1 second at 24fps

for i, video_path in enumerate({video_paths}):
    # Add movie strip
    bpy.ops.sequencer.movie_strip_add(filepath=video_path, frame_start=start_frame, channel=1)
    strip = bpy.context.scene.sequence_editor.active_strip
    strip.frame_final_end = start_frame + strip.frame_duration

    if i > 0:
        # Add fade to black before this scene
        bpy.ops.sequencer.effect_strip_add(type='COLOR', frame_start=start_frame - fade_duration, frame_end=start_frame, channel=2)
        color_strip = bpy.context.scene.sequence_editor.active_strip
        color_strip.color = (0, 0, 0)  # Black
        color_strip.blend_type = 'ALPHA_OVER'

    start_frame += strip.frame_duration

bpy.context.scene.frame_end = start_frame

# Render final movie
bpy.context.scene.render.filepath = '{output_path}'
bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.ffmpeg.audio_codec = 'AAC'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

bpy.ops.render.render(animation=True)
"""

    # Create output path
    output_dir = os.path.join(BASE_DIR, 'output')
    os.makedirs(output_dir, exist_ok=True)
    unique_name = str(uuid.uuid4()) + "_full.mp4"
    output_path = os.path.join(output_dir, unique_name)

    # Replace placeholders
    bpy_code = bpy_code.replace('{video_paths}', str(video_paths))
    bpy_code = bpy_code.replace('{output_path}', output_path)

    # Save and run
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(bpy_code)
        temp_script = f.name

    cmd = [blender_path, "--background", "--python", temp_script]
    subprocess.run(cmd)

    os.unlink(temp_script)
    return output_path