"""
VFX Pipeline Module - Visual effects processing using OpenCV and Blender integration.
Handles visual filters, post-processing, and Blender particle effects.
"""

import os
import cv2
import numpy as np
from typing import Optional, Dict, Tuple, List
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class VFXProcessor:
    """
    Video effects processor for color grading, filters, and post-processing.
    """

    def __init__(self):
        """Initialize VFX processor."""
        logger.info("VFXProcessor initialized")

    # ==================== Color Grading ====================

    def apply_lut_color_grade(self, frame: np.ndarray, lut_path: str) -> np.ndarray:
        """
        Apply color lookup table (LUT) for professional color grading.
        
        Args:
            frame: Input frame (BGR)
            lut_path: Path to LUT file (cube format)
            
        Returns:
            Color-graded frame
        """
        try:
            if not os.path.exists(lut_path):
                logger.warning(f"LUT file not found: {lut_path}")
                return frame
            
            # Load LUT (simplified - real LUT processing would be more complex)
            lut = np.load(lut_path) if lut_path.endswith('.npy') else None
            
            if lut is not None:
                # Apply LUT mapping (3D interpolation)
                frame_normalized = (frame.astype(np.float32) / 255.0 * (len(lut) - 1)).astype(np.int32)
                frame_normalized = np.clip(frame_normalized, 0, len(lut) - 1)
                
                graded = np.zeros_like(frame, dtype=np.uint8)
                for i in range(3):
                    graded[:, :, i] = (lut[frame_normalized[:, :, i]] * 255).astype(np.uint8)
                
                return graded
            
            return frame
            
        except Exception as e:
            logger.warning(f"Error applying LUT: {e}")
            return frame

    def apply_cinematic_color_grade(self, frame: np.ndarray, style: str = 'teal_orange') -> np.ndarray:
        """
        Apply cinematic color grading styles.
        
        Args:
            frame: Input frame (BGR)
            style: 'teal_orange', 'blue_yellow', 'desaturated', 'warm'
            
        Returns:
            Color-graded frame
        """
        frame_float = frame.astype(np.float32) / 255.0
        
        if style == 'teal_orange':
            # Teal shadows, orange highlights (popular cinematic look)
            # Shadows: boost blue
            shadow_mask = 1 - cv2.cvtColor((frame * 0.3).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
            frame_float[:, :, 0] = np.clip(frame_float[:, :, 0] + shadow_mask * 0.2, 0, 1)  # Blue
            
            # Highlights: boost red/yellow
            highlight_mask = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
            frame_float[:, :, 2] = np.clip(frame_float[:, :, 2] + highlight_mask * 0.15, 0, 1)  # Red
            frame_float[:, :, 1] = np.clip(frame_float[:, :, 1] + highlight_mask * 0.1, 0, 1)   # Green
        
        elif style == 'blue_yellow':
            # Blue shadows, yellow highlights
            shadow_mask = 1 - cv2.cvtColor((frame * 0.3).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
            frame_float[:, :, 0] = np.clip(frame_float[:, :, 0] + shadow_mask * 0.15, 0, 1)
            
            highlight_mask = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
            frame_float[:, :, 1] = np.clip(frame_float[:, :, 1] + highlight_mask * 0.2, 0, 1)
            frame_float[:, :, 2] = np.clip(frame_float[:, :, 2] + highlight_mask * 0.2, 0, 1)
        
        elif style == 'desaturated':
            # Reduce saturation for dramatic look
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[:, :, 1] *= 0.6  # Reduce saturation
            frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            frame_float = frame.astype(np.float32) / 255.0
        
        elif style == 'warm':
            # Warm, vintage look
            frame_float[:, :, 2] = np.clip(frame_float[:, :, 2] * 1.1, 0, 1)  # Red
            frame_float[:, :, 1] = np.clip(frame_float[:, :, 1] * 1.05, 0, 1) # Green
        
        return np.clip(frame_float * 255, 0, 255).astype(np.uint8)

    # ==================== Film & Grain ====================

    def apply_film_grain(self, frame: np.ndarray, grain_intensity: float = 0.05,
                        grain_color: bool = False) -> np.ndarray:
        """
        Apply realistic film grain effect.
        
        Args:
            frame: Input frame
            grain_intensity: Intensity of grain (0-1)
            grain_color: Whether to apply colored grain
            
        Returns:
            Frame with film grain
        """
        h, w = frame.shape[:2]
        
        # Generate grain
        if grain_color:
            grain = np.random.normal(0, grain_intensity * 50, (h, w, 3))
        else:
            grain = np.random.normal(0, grain_intensity * 50, (h, w, 1))
            grain = np.repeat(grain, 3, axis=2)
        
        # Apply Gaussian blur to grain for smoothness
        grain = cv2.GaussianBlur(grain, (3, 3), 0)
        
        # Blend grain with frame
        frame_float = frame.astype(np.float32)
        output = frame_float + grain
        
        return np.clip(output, 0, 255).astype(np.uint8)

    def apply_lens_distortion(self, frame: np.ndarray, distortion: float = 0.05) -> np.ndarray:
        """
        Apply lens distortion effect.
        
        Args:
            frame: Input frame
            distortion: Distortion amount (positive=barrel, negative=pincushion)
            
        Returns:
            Distorted frame
        """
        h, w = frame.shape[:2]
        
        # Create mesh grid
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        
        # Normalize coordinates to -1 to 1
        x_norm = (2 * x / w) - 1
        y_norm = (2 * y / h) - 1
        
        # Apply distortion
        r = np.sqrt(x_norm**2 + y_norm**2)
        factor = 1 + distortion * r**2
        
        x_distorted = (x_norm * factor * 0.5 + 0.5) * w
        y_distorted = (y_norm * factor * 0.5 + 0.5) * h
        
        # Remap
        x_distorted = np.clip(x_distorted, 0, w - 1)
        y_distorted = np.clip(y_distorted, 0, h - 1)
        
        output = cv2.remap(frame, x_distorted.astype(np.float32), 
                          y_distorted.astype(np.float32), cv2.INTER_LINEAR)
        
        return output

    # ==================== Motion Effects ====================

    def apply_motion_blur(self, frame: np.ndarray, direction: str = 'horizontal',
                         blur_amount: int = 15) -> np.ndarray:
        """
        Apply motion blur effect.
        
        Args:
            frame: Input frame
            direction: 'horizontal', 'vertical', or 'diagonal'
            blur_amount: Amount of blur (odd number)
            
        Returns:
            Motion-blurred frame
        """
        blur_amount = blur_amount if blur_amount % 2 == 1 else blur_amount + 1
        
        if direction == 'horizontal':
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (blur_amount, 1))
        elif direction == 'vertical':
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, blur_amount))
        else:  # diagonal
            kernel = np.eye(blur_amount, dtype=np.float32) / blur_amount
        
        output = cv2.filter2D(frame, -1, kernel)
        return output

    def apply_chromatic_aberration(self, frame: np.ndarray, offset: int = 3) -> np.ndarray:
        """
        Apply chromatic aberration effect (color channel separation).
        
        Args:
            frame: Input frame (BGR)
            offset: Pixel offset for each channel
            
        Returns:
            Frame with chromatic aberration
        """
        b, g, r = cv2.split(frame)
        
        # Shift channels
        b_shifted = np.roll(b, offset, axis=1)
        r_shifted = np.roll(r, -offset, axis=1)
        
        output = cv2.merge([b_shifted, g, r_shifted])
        return output

    # ==================== Edge & Detail Enhancement ====================

    def apply_unsharp_mask(self, frame: np.ndarray, amount: float = 1.0,
                          radius: int = 1, threshold: int = 0) -> np.ndarray:
        """
        Apply unsharp mask for detail enhancement.
        
        Args:
            frame: Input frame
            amount: Strength of sharpening
            radius: Blur radius for unsharp mask
            threshold: Minimum change to apply sharpening
            
        Returns:
            Sharpened frame
        """
        gaussian = cv2.GaussianBlur(frame, (radius * 2 + 1, radius * 2 + 1), 0)
        
        frame_float = frame.astype(np.float32)
        gaussian_float = gaussian.astype(np.float32)
        
        diff = frame_float - gaussian_float
        
        if threshold > 0:
            diff = np.where(np.abs(diff) >= threshold, diff, 0)
        
        output = frame_float + amount * diff
        
        return np.clip(output, 0, 255).astype(np.uint8)

    def apply_edge_enhance(self, frame: np.ndarray, strength: float = 1.0) -> np.ndarray:
        """
        Apply edge enhancement effect.
        
        Args:
            frame: Input frame
            strength: Enhancement strength
            
        Returns:
            Edge-enhanced frame
        """
        # Sobel edge detection
        sobelx = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalize edges
        edges = (edges / edges.max() * 255).astype(np.uint8)
        
        # Blend with original
        frame_float = frame.astype(np.float32)
        output = frame_float + edges[:, :, np.newaxis] * strength * 0.1
        
        return np.clip(output, 0, 255).astype(np.uint8)

    # ==================== Batch Processing ====================

    def process_video_with_vfx(self, input_path: str, output_path: str,
                              vfx_config: Dict) -> str:
        """
        Process entire video with VFX pipeline.
        
        Args:
            input_path: Input video path
            output_path: Output video path
            vfx_config: Dictionary with VFX settings:
                       {'color_grade': 'teal_orange', 'grain': 0.05, 'sharpness': 1.0, etc}
            
        Returns:
            Output video path
        """
        logger.info(f"Processing video with VFX: {input_path}")
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {input_path}")
        
        try:
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Apply color grading
                if 'color_grade' in vfx_config:
                    frame = self.apply_cinematic_color_grade(frame, vfx_config['color_grade'])
                
                # Apply grain
                if 'grain' in vfx_config:
                    frame = self.apply_film_grain(frame, vfx_config['grain'])
                
                # Apply sharpness
                if 'sharpness' in vfx_config:
                    frame = self.apply_unsharp_mask(frame, vfx_config['sharpness'])
                
                # Apply other effects
                if 'distortion' in vfx_config:
                    frame = self.apply_lens_distortion(frame, vfx_config['distortion'])
                
                if 'chromatic' in vfx_config:
                    frame = self.apply_chromatic_aberration(frame, vfx_config['chromatic'])
                
                out.write(frame)
                frame_count += 1
                
                if frame_count % 30 == 0:
                    logger.info(f"Processed {frame_count} frames")
            
            cap.release()
            out.release()
            
            logger.info(f"VFX processing complete: {output_path}")
            return output_path
            
        except Exception as e:
            cap.release()
            logger.error(f"Error processing video: {e}")
            raise


class BlenderParticleEffects:
    """
    Blender integration for particle effects (dust, smoke, etc).
    This module generates Blender Python scripts to add particle effects.
    """

    def __init__(self, blender_python_path: Optional[str] = None):
        """
        Initialize Blender particle effects generator.
        
        Args:
            blender_python_path: Path to Blender's Python environment
        """
        self.blender_python_path = blender_python_path
        logger.info("BlenderParticleEffects initialized")

    def generate_dust_particles_script(self, output_script: str, intensity: float = 1.0,
                                       particle_count: int = 5000) -> str:
        """
        Generate Blender script for dust particle effects.
        
        Args:
            output_script: Path to save script
            intensity: Dust density (0-1)
            particle_count: Number of particles
            
        Returns:
            Path to generated script
        """
        intensity = int(particle_count * intensity)
        
        script = f'''#!/usr/bin/env python3
import bpy
import random
from mathutils import Vector

# Clear default mesh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create emitter cube
bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 0))
emitter = bpy.context.active_object
emitter.name = "DustEmitter"

# Add particle system
particle_settings = bpy.data.particles.new(name="DustParticles")
particle_modifier = emitter.modifiers.new(name="DustModifier", type='PARTICLE_SYSTEM')
particle_modifier.particle_systems[0].settings = particle_settings

# Configure particle settings
ps = particle_settings
ps.count = {intensity}
ps.frame_start = 1
ps.frame_end = 250
ps.lifetime = 120
ps.lifetime_random = 0.3

# Emitter settings
ps.emit_from = 'FACE'
ps.use_rotations = True
ps.angular_velocity_factor = 0.5
ps.mass = 1.0

# Physics
ps.damping = 0.3
ps.drag_factor = 0.15
ps.brownian_factor = 0.5

# Render settings
ps.render_type = 'COLLECTION'
ps.use_collection_pick_random = False

print("Dust particle system created with {{}} particles".format({intensity}))
bpy.ops.wm.save_mainfile()
'''
        
        with open(output_script, 'w') as f:
            f.write(script)
        
        logger.info(f"Generated dust particles script: {output_script}")
        return output_script

    def generate_smoke_effects_script(self, output_script: str, intensity: float = 1.0) -> str:
        """
        Generate Blender script for smoke/exhaust effects.
        
        Args:
            output_script: Path to save script
            intensity: Smoke density (0-1)
            
        Returns:
            Path to generated script
        """
        script = f'''#!/usr/bin/env python3
import bpy
from mathutils import Vector

# Clear default mesh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create smoke emitter
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(0, 0, 2))
emitter = bpy.context.active_object
emitter.name = "SmokeEmitter"

# Add smoke modifier
smoke_mod = emitter.modifiers.new(name="SmokeModifier", type='SMOKE')
smoke_mod.smoke_type = 'FLOW'
smoke_mod.flow_settings.density = {intensity * 2}
smoke_mod.flow_settings.temperature = 2.0
smoke_mod.flow_settings.velocity_factor = 0.5

# Create domain
bpy.ops.mesh.primitive_cube_add(scale=15, location=(0, 0, 5))
domain = bpy.context.active_object
domain.name = "SmokeDomain"

smoke_domain = domain.modifiers.new(name="SmokeDomain", type='SMOKE')
smoke_domain.smoke_type = 'DOMAIN'

# Domain settings
domain_settings = smoke_domain.domain_settings
domain_settings.resolution_max = int(64 * {intensity})
domain_settings.clipping = 0.001
domain_settings.viscosity_base = 5.0
domain_settings.viscosity_exponent = 5.0

print("Smoke effect system created with intensity: {intensity}")
bpy.ops.wm.save_mainfile()
'''
        
        with open(output_script, 'w') as f:
            f.write(script)
        
        logger.info(f"Generated smoke effects script: {output_script}")
        return output_script

    def generate_fire_effects_script(self, output_script: str, intensity: float = 1.0) -> str:
        """
        Generate Blender script for fire effects.
        
        Args:
            output_script: Path to save script
            intensity: Fire intensity (0-1)
            
        Returns:
            Path to generated script
        """
        script = f'''#!/usr/bin/env python3
import bpy

# Clear default mesh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create fire emitter
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
emitter = bpy.context.active_object
emitter.name = "FireEmitter"

# Add particle system for flames
particle_settings = bpy.data.particles.new(name="FireParticles")
particle_modifier = emitter.modifiers.new(name="FireModifier", type='PARTICLE_SYSTEM')
particle_modifier.particle_systems[0].settings = particle_settings

ps = particle_settings
ps.count = int(10000 * {intensity})
ps.frame_start = 1
ps.frame_end = 250
ps.lifetime = 60
ps.lifetime_random = 0.2

# Physics
ps.damping = 0.1
ps.mass = 0.5
ps.use_rotations = True
ps.angular_velocity_factor = 2.0

# Render settings
ps.render_type = 'OBJECT'

print("Fire effect system created with intensity: {intensity}")
bpy.ops.wm.save_mainfile()
'''
        
        with open(output_script, 'w') as f:
            f.write(script)
        
        logger.info(f"Generated fire effects script: {output_script}")
        return output_script

    def generate_vehicle_effects_script(self, output_script: str, vehicle_type: str = 'truck',
                                       intensity: float = 1.0) -> str:
        """
        Generate Blender script for vehicle-specific effects (exhaust, etc).
        
        Args:
            output_script: Path to save script
            vehicle_type: 'truck', 'forklift', etc
            intensity: Effect intensity
            
        Returns:
            Path to generated script
        """
        if vehicle_type.lower() == 'truck':
            particle_count = int(3000 * intensity)
            emitter_scale = 1.5
            emitter_loc = Vector((0, 0, 3))
        elif vehicle_type.lower() == 'forklift':
            particle_count = int(1500 * intensity)
            emitter_scale = 0.8
            emitter_loc = Vector((0, 0, 1.5))
        else:
            particle_count = int(2000 * intensity)
            emitter_scale = 1.0
            emitter_loc = Vector((0, 0, 2))
        
        script = f'''#!/usr/bin/env python3
import bpy
from mathutils import Vector

# Clear default mesh
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create exhaust emitter
bpy.ops.mesh.primitive_cylinder_add(radius={emitter_scale * 0.3}, depth=0.5, 
                                    location=Vector((0, 0, 3)))
emitter = bpy.context.active_object
emitter.name = "{vehicle_type}_ExhaustEmitter"

# Add particle system
particle_settings = bpy.data.particles.new(name="{vehicle_type}_Exhaust")
particle_modifier = emitter.modifiers.new(name="ExhaustModifier", type='PARTICLE_SYSTEM')
particle_modifier.particle_systems[0].settings = particle_settings

ps = particle_settings
ps.count = {particle_count}
ps.frame_start = 1
ps.frame_end = 250
ps.lifetime = 100
ps.lifetime_random = 0.4

# Physics - smoke/exhaust like behavior
ps.damping = 0.2
ps.mass = 0.8
ps.drag_factor = 0.2
ps.brown_ponent = 0.1
ps.effector_weights.gravity = 0.3

# Velocity
ps.initial_velocity_factor = 2.0
ps.velocity_factor_random = 0.3

print("{vehicle_type} exhaust effect created with {{}} particles".format({particle_count}))
bpy.ops.wm.save_mainfile()
'''
        
        with open(output_script, 'w') as f:
            f.write(script)
        
        logger.info(f"Generated {vehicle_type} effects script: {output_script}")
        return output_script
