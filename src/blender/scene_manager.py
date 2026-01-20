"""
Universal Scene Setup Manager
Flexible scene configuration system for any type of scene
Provides full control over scene properties, objects, lighting, and cameras
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SceneObject:
    """Represents an object in the scene"""
    name: str
    type: str  # 'character', 'prop', 'light', 'camera', 'environment'
    position: tuple = (0, 0, 0)
    rotation: tuple = (0, 0, 0)
    scale: tuple = (1, 1, 1)
    color: Optional[str] = None
    material: Optional[str] = None
    animation: Optional[Dict] = None
    properties: Optional[Dict] = None


@dataclass
class Camera:
    """Camera configuration"""
    name: str
    position: tuple = (0, -10, 5)
    rotation: tuple = (0, 0, 0)
    focal_length: float = 50.0
    look_at: Optional[str] = None  # Target object name
    fov: float = 50.0


@dataclass
class LightSource:
    """Light configuration"""
    name: str
    type: str  # 'SUN', 'POINT', 'AREA', 'SPOT'
    position: tuple = (0, 0, 10)
    energy: float = 2.0
    color: tuple = (1.0, 1.0, 1.0)
    intensity: float = 1.0
    rotation: tuple = (0, 0, 0)


@dataclass
class SceneConfig:
    """Complete scene configuration"""
    name: str
    description: str
    duration: float  # seconds
    fps: int = 30
    resolution: tuple = (1920, 1080)  # (width, height)
    
    # Scene elements
    objects: List[SceneObject] = None
    camera: Optional[Camera] = None
    lights: List[LightSource] = None
    
    # Environment
    background_color: tuple = (0.1, 0.1, 0.1)
    ambient_light_strength: float = 0.5
    world_type: str = 'color'  # 'color', 'hdri', 'gradient'
    
    # Effects
    color_grading: Optional[Dict] = None  # {'temp': 'warm', 'saturation': 0.8}
    bloom: bool = False
    motion_blur: bool = False
    depth_of_field: bool = False
    
    # Rendering
    render_engine: str = 'EEVEE'  # 'EEVEE' or 'CYCLES'
    samples: int = 64
    use_gpu: bool = True
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.lights is None:
            self.lights = []


class SceneSetupManager:
    """
    Manages scene setup and configuration
    Allows creation of custom scenes without hardcoded warehouse setup
    """
    
    # Predefined scene templates
    SCENE_TEMPLATES = {
        'empty': {
            'description': 'Empty scene with default lighting',
            'objects': [],
            'lights': [
                {
                    'name': 'Key Light',
                    'type': 'SUN',
                    'position': (5, 5, 10),
                    'energy': 2.0,
                    'color': (1.0, 0.95, 0.8)
                }
            ]
        },
        'office': {
            'description': 'Modern office environment',
            'objects': [
                {'name': 'Desk', 'type': 'prop', 'position': (0, 0, 0), 'color': '#8B4513'},
                {'name': 'Chair', 'type': 'prop', 'position': (0, -1, 0), 'color': '#333333'},
                {'name': 'Monitor', 'type': 'prop', 'position': (0.5, 0, 1), 'color': '#000000'},
                {'name': 'Lamp', 'type': 'light', 'position': (0, 0, 2), 'color': '#FFFF99'}
            ],
            'lights': [
                {'name': 'Ceiling', 'type': 'AREA', 'position': (0, 0, 4), 'energy': 1.5},
                {'name': 'Window', 'type': 'SUN', 'position': (5, 5, 5), 'energy': 1.0}
            ],
            'background_color': (0.95, 0.95, 0.95)
        },
        'studio': {
            'description': 'Professional studio setup',
            'objects': [],
            'lights': [
                {'name': 'Key Light', 'type': 'AREA', 'position': (-3, -5, 4), 'energy': 2.0},
                {'name': 'Fill Light', 'type': 'AREA', 'position': (3, -5, 3), 'energy': 1.0},
                {'name': 'Back Light', 'type': 'POINT', 'position': (0, 5, 5), 'energy': 1.5}
            ],
            'background_color': (0.5, 0.5, 0.5),
            'color_grading': {'temp': 'cool', 'saturation': 0.9}
        },
        'outdoor': {
            'description': 'Outdoor natural environment',
            'objects': [
                {'name': 'Ground', 'type': 'environment', 'color': '#90EE90'},
                {'name': 'Sky', 'type': 'environment', 'color': '#87CEEB'}
            ],
            'lights': [
                {'name': 'Sun', 'type': 'SUN', 'position': (10, 10, 10), 'energy': 3.0, 'color': (1.0, 0.95, 0.8)},
                {'name': 'Sky', 'type': 'SUN', 'position': (-5, -5, 3), 'energy': 0.5, 'color': (0.8, 0.9, 1.0)}
            ],
            'background_color': (0.7, 0.85, 1.0),
            'ambient_light_strength': 0.7
        },
        'dark_dramatic': {
            'description': 'Dark dramatic scene',
            'objects': [],
            'lights': [
                {'name': 'Key Light', 'type': 'SPOT', 'position': (-5, -5, 5), 'energy': 2.5},
                {'name': 'Fill Light', 'type': 'POINT', 'position': (5, 5, 2), 'energy': 0.3}
            ],
            'background_color': (0.05, 0.05, 0.05),
            'color_grading': {'temp': 'warm', 'saturation': 0.7},
            'bloom': True
        }
    }
    
    # Lighting presets for different moods
    LIGHTING_PRESETS = {
        'soft': {
            'ambient_strength': 0.7,
            'lights': [
                {'type': 'AREA', 'position': (-3, -3, 5), 'energy': 1.5},
                {'type': 'AREA', 'position': (3, -3, 4), 'energy': 1.0}
            ]
        },
        'dramatic': {
            'ambient_strength': 0.3,
            'lights': [
                {'type': 'SPOT', 'position': (-5, -5, 6), 'energy': 2.5},
                {'type': 'POINT', 'position': (3, 3, 2), 'energy': 0.4}
            ]
        },
        'natural': {
            'ambient_strength': 0.6,
            'lights': [
                {'type': 'SUN', 'position': (5, 5, 8), 'energy': 2.0, 'color': (1.0, 0.95, 0.8)},
                {'type': 'SUN', 'position': (-5, -5, 3), 'energy': 0.5, 'color': (0.8, 0.9, 1.0)}
            ]
        },
        'cinematic': {
            'ambient_strength': 0.4,
            'lights': [
                {'type': 'AREA', 'position': (-4, -4, 6), 'energy': 2.0, 'color': (1.0, 0.95, 0.7)},
                {'type': 'AREA', 'position': (4, -4, 3), 'energy': 0.8, 'color': (0.7, 0.9, 1.0)},
                {'type': 'POINT', 'position': (0, 5, 3), 'energy': 0.5}
            ]
        }
    }
    
    # Color grading presets
    COLOR_GRADING_PRESETS = {
        'neutral': {'temp': 0, 'saturation': 1.0, 'contrast': 1.0},
        'warm': {'temp': 0.3, 'saturation': 1.1, 'contrast': 1.0},
        'cool': {'temp': -0.3, 'saturation': 1.0, 'contrast': 1.0},
        'cinematic': {'temp': 0.1, 'saturation': 0.9, 'contrast': 1.1},
        'vintage': {'temp': 0.2, 'saturation': 0.7, 'contrast': 0.9},
        'noir': {'temp': -0.1, 'saturation': 0.5, 'contrast': 1.3}
    }
    
    def __init__(self):
        """Initialize scene setup manager"""
        self.scenes: Dict[str, SceneConfig] = {}
        self.current_scene: Optional[SceneConfig] = None
        logger.info("SceneSetupManager initialized")
    
    def create_custom_scene(self, 
                           name: str,
                           description: str,
                           duration: float,
                           template: Optional[str] = None,
                           **kwargs) -> SceneConfig:
        """
        Create a custom scene configuration
        
        Args:
            name: Scene name
            description: Scene description
            duration: Duration in seconds
            template: Base template name ('empty', 'office', 'studio', 'outdoor', 'dark_dramatic')
            **kwargs: Additional scene properties
            
        Returns:
            SceneConfig object
        """
        
        # Start with template if provided
        config_dict = {}
        if template and template in self.SCENE_TEMPLATES:
            template_data = self.SCENE_TEMPLATES[template]
            config_dict.update(template_data)
        
        # Create base config
        config = SceneConfig(
            name=name,
            description=description,
            duration=duration,
            **kwargs
        )
        
        # Apply template settings
        if template and template in self.SCENE_TEMPLATES:
            template_data = self.SCENE_TEMPLATES[template]
            
            # Add objects from template
            for obj_data in template_data.get('objects', []):
                config.objects.append(SceneObject(**obj_data))
            
            # Add lights from template
            for light_data in template_data.get('lights', []):
                config.lights.append(LightSource(**light_data))
            
            # Apply template settings
            if 'background_color' in template_data:
                config.background_color = template_data['background_color']
            if 'color_grading' in template_data:
                config.color_grading = template_data['color_grading']
        
        self.scenes[name] = config
        self.current_scene = config
        logger.info(f"Created scene: {name}")
        
        return config
    
    def apply_lighting_preset(self, scene_name: str, preset: str) -> bool:
        """
        Apply a lighting preset to a scene
        
        Args:
            scene_name: Scene name
            preset: 'soft', 'dramatic', 'natural', 'cinematic'
            
        Returns:
            Success status
        """
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        if preset not in self.LIGHTING_PRESETS:
            logger.error(f"Lighting preset not found: {preset}")
            return False
        
        scene = self.scenes[scene_name]
        preset_data = self.LIGHTING_PRESETS[preset]
        
        # Update ambient light
        scene.ambient_light_strength = preset_data['ambient_strength']
        
        # Replace lights
        scene.lights = []
        for light_data in preset_data['lights']:
            scene.lights.append(LightSource(
                name=f"{preset.capitalize()} Light",
                **light_data
            ))
        
        logger.info(f"Applied lighting preset '{preset}' to scene '{scene_name}'")
        return True
    
    def apply_color_grading_preset(self, scene_name: str, preset: str) -> bool:
        """
        Apply a color grading preset
        
        Args:
            scene_name: Scene name
            preset: 'neutral', 'warm', 'cool', 'cinematic', 'vintage', 'noir'
            
        Returns:
            Success status
        """
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        if preset not in self.COLOR_GRADING_PRESETS:
            logger.error(f"Color grading preset not found: {preset}")
            return False
        
        scene = self.scenes[scene_name]
        scene.color_grading = self.COLOR_GRADING_PRESETS[preset]
        
        logger.info(f"Applied color grading preset '{preset}' to scene '{scene_name}'")
        return True
    
    def add_object_to_scene(self, 
                           scene_name: str,
                           obj: SceneObject) -> bool:
        """Add an object to a scene"""
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        self.scenes[scene_name].objects.append(obj)
        logger.info(f"Added object '{obj.name}' to scene '{scene_name}'")
        return True
    
    def add_light_to_scene(self,
                          scene_name: str,
                          light: LightSource) -> bool:
        """Add a light to a scene"""
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        self.scenes[scene_name].lights.append(light)
        logger.info(f"Added light '{light.name}' to scene '{scene_name}'")
        return True
    
    def configure_camera(self,
                        scene_name: str,
                        camera: Camera) -> bool:
        """Configure scene camera"""
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        self.scenes[scene_name].camera = camera
        logger.info(f"Configured camera for scene '{scene_name}'")
        return True
    
    def list_templates(self) -> List[str]:
        """List available templates"""
        return list(self.SCENE_TEMPLATES.keys())
    
    def list_lighting_presets(self) -> List[str]:
        """List available lighting presets"""
        return list(self.LIGHTING_PRESETS.keys())
    
    def list_color_grading_presets(self) -> List[str]:
        """List available color grading presets"""
        return list(self.COLOR_GRADING_PRESETS.keys())
    
    def get_scene(self, scene_name: str) -> Optional[SceneConfig]:
        """Get a scene configuration"""
        return self.scenes.get(scene_name)
    
    def get_all_scenes(self) -> Dict[str, SceneConfig]:
        """Get all scenes"""
        return self.scenes
    
    def export_scene(self, scene_name: str, output_path: str) -> bool:
        """Export scene configuration to JSON"""
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        scene = self.scenes[scene_name]
        scene_dict = asdict(scene)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(scene_dict, f, indent=2)
            logger.info(f"Exported scene '{scene_name}' to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting scene: {e}")
            return False
    
    def import_scene(self, json_path: str, scene_name: Optional[str] = None) -> bool:
        """Import scene configuration from JSON"""
        try:
            with open(json_path, 'r') as f:
                scene_dict = json.load(f)
            
            name = scene_name or scene_dict.get('name', 'imported_scene')
            config = SceneConfig(**scene_dict)
            self.scenes[name] = config
            
            logger.info(f"Imported scene from {json_path}")
            return True
        except Exception as e:
            logger.error(f"Error importing scene: {e}")
            return False
    
    def delete_scene(self, scene_name: str) -> bool:
        """Delete a scene"""
        if scene_name not in self.scenes:
            logger.error(f"Scene not found: {scene_name}")
            return False
        
        del self.scenes[scene_name]
        if self.current_scene and self.current_scene.name == scene_name:
            self.current_scene = None
        
        logger.info(f"Deleted scene '{scene_name}'")
        return True
    
    def clone_scene(self, source_name: str, target_name: str) -> bool:
        """Clone an existing scene"""
        if source_name not in self.scenes:
            logger.error(f"Source scene not found: {source_name}")
            return False
        
        import copy
        source = self.scenes[source_name]
        cloned = copy.deepcopy(source)
        cloned.name = target_name
        
        self.scenes[target_name] = cloned
        logger.info(f"Cloned scene '{source_name}' to '{target_name}'")
        return True
    
    def get_scene_info(self, scene_name: str) -> Optional[Dict]:
        """Get detailed scene information"""
        if scene_name not in self.scenes:
            return None
        
        scene = self.scenes[scene_name]
        return {
            'name': scene.name,
            'description': scene.description,
            'duration': scene.duration,
            'objects_count': len(scene.objects),
            'lights_count': len(scene.lights),
            'resolution': scene.resolution,
            'render_engine': scene.render_engine,
            'has_camera': scene.camera is not None,
            'background_color': scene.background_color,
            'color_grading': scene.color_grading
        }
    
    def print_scene_summary(self, scene_name: str):
        """Print a formatted summary of a scene"""
        info = self.get_scene_info(scene_name)
        if not info:
            print(f"Scene '{scene_name}' not found")
            return
        
        print(f"\n{'='*60}")
        print(f"SCENE: {info['name']}")
        print(f"{'='*60}")
        print(f"Description: {info['description']}")
        print(f"Duration: {info['duration']:.1f} seconds")
        print(f"Resolution: {info['resolution'][0]}x{info['resolution'][1]}")
        print(f"Objects: {info['objects_count']}")
        print(f"Lights: {info['lights_count']}")
        print(f"Render Engine: {info['render_engine']}")
        print(f"Camera: {'Yes' if info['has_camera'] else 'No'}")
        print(f"Background Color: {info['background_color']}")
        print(f"Color Grading: {info['color_grading']}")
        print(f"{'='*60}\n")


# Example usage
if __name__ == "__main__":
    manager = SceneSetupManager()
    
    # Create scenes from templates
    print("Available templates:", manager.list_templates())
    print("Available lighting presets:", manager.list_lighting_presets())
    print("Available color grading:", manager.list_color_grading_presets())
    
    # Create custom scenes
    manager.create_custom_scene(
        name="My Office",
        description="A modern office environment",
        duration=10,
        template="office"
    )
    
    manager.create_custom_scene(
        name="Studio Setup",
        description="Professional studio",
        duration=5,
        template="studio"
    )
    
    # Customize scenes
    manager.apply_lighting_preset("My Office", "natural")
    manager.apply_color_grading_preset("My Office", "cinematic")
    
    # Print summary
    manager.print_scene_summary("My Office")
    manager.print_scene_summary("Studio Setup")
