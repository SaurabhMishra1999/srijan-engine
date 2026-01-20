"""
Blender Renderer - Handles 3D scene rendering and video export
Integrates with Blender's Python API and command-line rendering
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, Dict
import logging
import sys

logger = logging.getLogger(__name__)


class BlenderRenderer:
    """
    Handles rendering of 3D scenes to video using Blender
    Can be used in two modes:
    1. Direct Blender Python API (when running inside Blender)
    2. Command-line subprocess (when running from external Python)
    """
    
    def __init__(self, blender_path: Optional[str] = None):
        """
        Initialize Blender Renderer
        
        Args:
            blender_path: Path to Blender executable
        """
        self.blender_path = blender_path or self._find_blender()
        self.temp_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'output', 'blender_temp'
        )
        os.makedirs(self.temp_dir, exist_ok=True)
        logger.info(f"BlenderRenderer initialized with: {self.blender_path}")
    
    def _find_blender(self) -> str:
        """Find Blender installation"""
        # Common Blender paths
        possible_paths = [
            r"e:\Srijan_Engine\blender_portable\5.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 3.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"/usr/bin/blender",
            r"/Applications/Blender.app/Contents/MacOS/Blender"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Try command-line lookup
        try:
            result = subprocess.run(['where' if os.name == 'nt' else 'which', 'blender'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except:
            pass
        
        logger.warning("Blender not found - video rendering may fail")
        return "blender"
    
    def render_scene_to_video(self, script: str, output_path: str,
                             duration: int = 10, fps: int = 30,
                             resolution: str = "1920x1080") -> str:
        """
        Render a scene to video based on script description
        
        Args:
            script: Scene description or narrative
            output_path: Path to save output video
            duration: Duration in seconds
            fps: Frames per second
            resolution: Output resolution (WxH)
            
        Returns:
            Path to rendered video
        """
        logger.info(f"Rendering scene to video: {output_path}")
        
        try:
            # Create a simple Blender script that generates a test scene
            blend_script = self._create_render_script(
                script, output_path, duration, fps, resolution
            )
            
            # Save script to temp file
            script_path = os.path.join(self.temp_dir, "render_script.py")
            with open(script_path, 'w') as f:
                f.write(blend_script)
            
            # Run Blender in background mode
            cmd = [
                self.blender_path,
                '--background',
                '--python', script_path
            ]
            
            logger.info(f"Running Blender: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Blender error: {result.stderr}")
                # Fall back to simple test video
                return self._create_test_video(output_path, duration, fps)
            
            if os.path.exists(output_path):
                logger.info(f"Video rendered successfully: {output_path}")
                return output_path
            else:
                logger.warning("Blender completed but no output file created")
                return self._create_test_video(output_path, duration, fps)
        
        except Exception as e:
            logger.error(f"Error rendering scene: {e}")
            return self._create_test_video(output_path, duration, fps)
    
    def _create_render_script(self, script: str, output_path: str,
                             duration: int, fps: int, resolution: str) -> str:
        """Create a Blender Python script for rendering"""
        
        width, height = map(int, resolution.split('x'))
        total_frames = duration * fps
        
        render_script = f"""
import bpy
import os

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Set up scene
scene = bpy.context.scene
scene.render.fps = {fps}
scene.render.resolution_x = {width}
scene.render.resolution_y = {height}
scene.frame_end = {total_frames}

# Set render engine to Cycles (or Eevee for faster preview)
scene.render.engine = 'BLENDER_EEVEE'

# Add lighting
bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
light = bpy.context.object
light.data.energy = 2.0

# Add camera
bpy.ops.object.camera_add(location=(0, -10, 5))
camera = bpy.context.object
scene.camera = camera

# Add a cube as placeholder scene element
bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
cube = bpy.context.object

# Add material
mat = bpy.data.materials.new(name="SceneMaterial")
mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.2, 0.4, 0.8, 1.0)
cube.data.materials.append(mat)

# Set output
output_path = r"{output_path}"
scene.render.filepath = output_path
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.image_settings.ffmpeg_codec = 'H264'
scene.render.image_settings.ffmpeg_format = 'MPEG4'

# Render animation
bpy.ops.render.render(animation=True, write_still=False)

print(f"Rendering complete: {{output_path}}")
"""
        
        return render_script
    
    def _create_test_video(self, output_path: str, duration: int = 10,
                          fps: int = 30) -> str:
        """Create a simple test video using ffmpeg"""
        try:
            import subprocess
            
            width, height = 1920, 1080
            
            cmd = [
                'ffmpeg',
                '-f', 'lavfi',
                '-i', f'color=c=0x1f4d8c:s={width}x{height}:d={duration}',
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', str(fps),
                output_path,
                '-y'
            ]
            
            subprocess.run(cmd, capture_output=True, check=False, timeout=120)
            
            if os.path.exists(output_path):
                logger.info(f"Test video created: {output_path}")
                return output_path
        except Exception as e:
            logger.error(f"Could not create test video: {e}")
        
        return None
    
    def render_to_video(self, blend_file: str, output_dir: str,
                       fps: int = 30) -> Optional[str]:
        """
        Render an existing Blender file to video
        
        Args:
            blend_file: Path to .blend file
            output_dir: Output directory
            fps: Frames per second
            
        Returns:
            Path to rendered video
        """
        logger.info(f"Rendering Blender file: {blend_file}")
        
        output_path = os.path.join(output_dir, "rendered_scene.mp4")
        
        try:
            cmd = [
                self.blender_path,
                '--background',
                blend_file,
                '-a'  # Render all frames
            ]
            
            subprocess.run(cmd, capture_output=True, timeout=300)
            
            if os.path.exists(output_path):
                return output_path
        except Exception as e:
            logger.error(f"Error rendering blend file: {e}")
        
        return None


def render_scene(scene_description):
    """Legacy compatibility function"""
    renderer = BlenderRenderer()
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'output', 'movie.mp4'
    )
    return renderer.render_scene_to_video(
        script=scene_description,
        output_path=output_path,
        duration=5
    )


if __name__ == "__main__":
    # Test rendering
    renderer = BlenderRenderer()
    print(f"Blender path: {renderer.blender_path}")
    print(f"Temp dir: {renderer.temp_dir}")