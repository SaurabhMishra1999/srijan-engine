"""
AI Script Processor - Converts narrative scripts into 3D scene configurations
Parses text to extract scenes, camera angles, lighting, and object descriptions
"""

import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class SceneObject:
    """Represents an object in a scene"""
    name: str
    type: str  # 'character', 'prop', 'environment'
    position: tuple = (0, 0, 0)
    scale: tuple = (1, 1, 1)
    rotation: tuple = (0, 0, 0)
    color: Optional[str] = None
    material: Optional[str] = None


@dataclass
class Scene:
    """Represents a single scene"""
    id: int
    description: str
    duration: float
    camera_angle: str  # 'wide', 'close-up', 'overhead', 'side'
    camera_position: tuple = (0, 5, 10)
    lighting: str = 'soft'  # 'soft', 'hard', 'dramatic', 'natural'
    background: Optional[str] = None
    objects: List[SceneObject] = None
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = []


class ScriptProcessor:
    """
    Processes narrative scripts and converts them to 3D scene configurations
    for Blender rendering
    """
    
    # Keywords for scene detection
    SCENE_KEYWORDS = ['scene', 'location', 'setting', 'place', 'room', 'area', 'environment']
    CAMERA_KEYWORDS = {
        'close-up': ['close', 'close-up', 'closeup', 'tight', 'zoom'],
        'wide': ['wide', 'wide shot', 'establish', 'establishing', 'full', 'panorama'],
        'overhead': ['overhead', 'bird\'s eye', 'top-down', 'aerial'],
        'side': ['side', 'profile', 'angle', 'perspective']
    }
    
    LIGHTING_KEYWORDS = {
        'soft': ['soft', 'gentle', 'diffuse', 'ambient'],
        'hard': ['harsh', 'bright', 'intense', 'sharp'],
        'dramatic': ['dramatic', 'cinematic', 'theatrical', 'moody'],
        'natural': ['natural', 'daylight', 'sunlight', 'outdoor']
    }
    
    def __init__(self):
        """Initialize the script processor"""
        self.scenes: List[Scene] = []
        self.global_config = {
            'fps': 30,
            'resolution': '1920x1080',
            'color_space': 'sRGB'
        }
        logger.info("ScriptProcessor initialized")
    
    def parse_script_to_scenes(self, script: str) -> Dict:
        """
        Parse a narrative script into structured scene configuration
        
        Args:
            script: Narrative script text
            
        Returns:
            Dictionary with scene configuration for Blender
        """
        self.scenes = []
        
        # Split script into sentences/paragraphs
        paragraphs = [p.strip() for p in script.split('\n\n') if p.strip()]
        
        scene_id = 1
        for paragraph in paragraphs:
            scene = self._parse_paragraph_to_scene(paragraph, scene_id)
            if scene:
                self.scenes.append(scene)
                scene_id += 1
        
        # If no scenes detected, create a default one
        if not self.scenes:
            self.scenes.append(Scene(
                id=1,
                description=script[:200],
                duration=5,
                camera_angle='wide',
                lighting='soft'
            ))
        
        # Return structured configuration
        return self._serialize_scenes_config()
    
    def _parse_paragraph_to_scene(self, paragraph: str, scene_id: int) -> Optional[Scene]:
        """Parse a paragraph into a scene"""
        
        # Extract camera angle
        camera_angle = self._extract_camera_angle(paragraph)
        
        # Extract lighting
        lighting = self._extract_lighting(paragraph)
        
        # Extract background/setting
        background = self._extract_background(paragraph)
        
        # Extract objects/characters
        objects = self._extract_objects(paragraph)
        
        # Estimate duration based on text length (rough estimate)
        duration = min(5, max(1, len(paragraph.split()) / 20))
        
        scene = Scene(
            id=scene_id,
            description=paragraph,
            duration=duration,
            camera_angle=camera_angle,
            lighting=lighting,
            background=background,
            objects=objects
        )
        
        logger.info(f"Parsed scene {scene_id}: {camera_angle} camera, {lighting} lighting")
        return scene
    
    def _extract_camera_angle(self, text: str) -> str:
        """Extract camera angle from text"""
        text_lower = text.lower()
        
        for angle, keywords in self.CAMERA_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return angle
        
        return 'wide'  # Default
    
    def _extract_lighting(self, text: str) -> str:
        """Extract lighting style from text"""
        text_lower = text.lower()
        
        for lighting, keywords in self.LIGHTING_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return lighting
        
        return 'soft'  # Default
    
    def _extract_background(self, text: str) -> Optional[str]:
        """Extract background/setting from text"""
        # Look for common location keywords
        locations = ['warehouse', 'office', 'street', 'park', 'forest', 'building',
                    'room', 'garden', 'beach', 'mountain', 'city', 'house', 'shop']
        
        text_lower = text.lower()
        for location in locations:
            if location in text_lower:
                return location
        
        return None
    
    def _extract_objects(self, text: str) -> List[SceneObject]:
        """Extract objects and characters from text"""
        objects = []
        
        # Common object patterns
        patterns = {
            'character': [r'\b(person|character|man|woman|boy|girl|character|actor)\b'],
            'prop': [r'\b(table|chair|desk|box|computer|phone|camera|object)\b'],
            'environment': [r'\b(tree|building|wall|floor|ceiling|sky)\b']
        }
        
        for obj_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    obj = SceneObject(
                        name=match.lower(),
                        type=obj_type,
                        position=(0, 0, 0) if obj_type != 'character' else (0, 0, -5)
                    )
                    objects.append(obj)
        
        return objects
    
    def _serialize_scenes_config(self) -> Dict:
        """Serialize scenes to configuration dictionary"""
        return {
            'scenes': [
                {
                    'id': scene.id,
                    'description': scene.description,
                    'duration': scene.duration,
                    'camera': {
                        'angle': scene.camera_angle,
                        'position': scene.camera_position,
                    },
                    'lighting': scene.lighting,
                    'background': scene.background,
                    'objects': [
                        {
                            'name': obj.name,
                            'type': obj.type,
                            'position': obj.position,
                            'scale': obj.scale,
                            'color': obj.color
                        }
                        for obj in scene.objects
                    ]
                }
                for scene in self.scenes
            ],
            'global_config': self.global_config,
            'total_duration': sum(s.duration for s in self.scenes)
        }
    
    def process_script(self, script: str) -> str:
        """Legacy function name - alias for parse_script_to_scenes"""
        config = self.parse_script_to_scenes(script)
        return json.dumps(config, indent=2)


def process_script(script):
    """Placeholder compatibility function"""
    processor = ScriptProcessor()
    return f"Scene based on: {script[:50]}..."