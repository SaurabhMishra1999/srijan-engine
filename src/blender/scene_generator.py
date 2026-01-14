import subprocess
import os
import tempfile
import uuid

def render_scene(bpy_code, blender_path):
    """
    Renders the scene using the provided bpy_code and Blender executable.
    Saves the output as a unique .mp4 file in the output/ folder.
    """
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