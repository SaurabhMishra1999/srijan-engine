"""
Warehouse Assets Manager - Manages 3D assets for the Saipooja Warehouse project.
Handles inventory of forklifts, medicine boxes, container trucks, and other warehouse equipment.
"""

import os
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class AssetType(Enum):
    """Enum for asset types."""
    FORKLIFT = "forklift"
    MEDICINE_BOX = "medicine_box"
    CONTAINER_TRUCK = "container_truck"
    SHELF = "shelf"
    PALLET = "pallet"
    WAREHOUSE_STRUCTURE = "warehouse_structure"
    LIGHTING = "lighting"
    CAMERA = "camera"
    PARTICLE_SYSTEM = "particle_system"


@dataclass
class Asset3D:
    """Represents a 3D asset."""
    asset_id: str
    name: str
    asset_type: AssetType
    model_path: str
    scale: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    position: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    texture_path: Optional[str] = None
    material_name: Optional[str] = None
    physics_enabled: bool = False
    animation_path: Optional[str] = None
    metadata: Dict = None

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        d = asdict(self)
        d['asset_type'] = self.asset_type.value
        return d


@dataclass
class WarehouseScene:
    """Represents a warehouse scene configuration."""
    scene_name: str
    scene_id: str
    description: str
    assets: List[Asset3D]
    duration: float = 5.0  # Duration in seconds
    frame_rate: int = 30
    resolution: Tuple[int, int] = (1920, 1080)
    lighting_config: Dict = None
    camera_config: Dict = None
    physics_enabled: bool = True


class WarehouseAssetsManager:
    """
    Manages 3D assets and scenes for warehouse-themed content.
    Handles asset inventory, scene creation, and asset configuration.
    """

    def __init__(self, assets_dir: Optional[str] = None):
        """
        Initialize warehouse assets manager.
        
        Args:
            assets_dir: Directory to store asset data
        """
        if assets_dir is None:
            assets_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'assets', 'models'
            )
        
        self.assets_dir = assets_dir
        self.asset_registry: Dict[str, Asset3D] = {}
        self.scenes: Dict[str, WarehouseScene] = {}
        
        os.makedirs(assets_dir, exist_ok=True)
        
        # Initialize default warehouse assets
        self._init_default_assets()
        
        logger.info(f"WarehouseAssetsManager initialized with assets dir: {assets_dir}")

    def _init_default_assets(self):
        """Initialize default warehouse assets."""
        default_assets = [
            Asset3D(
                asset_id="forklift_001",
                name="Standard Forklift",
                asset_type=AssetType.FORKLIFT,
                model_path=os.path.join(self.assets_dir, "models", "forklift.blend"),
                scale=(1.0, 1.0, 1.0),
                physics_enabled=True,
                metadata={
                    "capacity": "2500kg",
                    "lift_height": "6m",
                    "brand": "Toyota"
                }
            ),
            Asset3D(
                asset_id="medicine_box_001",
                name="Medical Boxes Stack",
                asset_type=AssetType.MEDICINE_BOX,
                model_path=os.path.join(self.assets_dir, "models", "medicine_box.blend"),
                scale=(1.0, 1.0, 1.0),
                physics_enabled=True,
                metadata={
                    "dimensions": "400x300x200mm",
                    "material": "cardboard",
                    "stackable": True
                }
            ),
            Asset3D(
                asset_id="container_truck_001",
                name="Container Truck",
                asset_type=AssetType.CONTAINER_TRUCK,
                model_path=os.path.join(self.assets_dir, "models", "container_truck.blend"),
                scale=(1.0, 1.0, 1.0),
                physics_enabled=True,
                metadata={
                    "capacity": "20000kg",
                    "container_size": "40ft",
                    "engine_sound": "truck_engine.wav"
                }
            ),
            Asset3D(
                asset_id="warehouse_shelf_001",
                name="Industrial Shelf",
                asset_type=AssetType.SHELF,
                model_path=os.path.join(self.assets_dir, "models", "warehouse_shelf.blend"),
                scale=(1.0, 1.0, 1.0),
                physics_enabled=False,
                metadata={
                    "height": "2.5m",
                    "shelves": 4,
                    "material": "steel"
                }
            ),
            Asset3D(
                asset_id="pallet_001",
                name="Wooden Pallet",
                asset_type=AssetType.PALLET,
                model_path=os.path.join(self.assets_dir, "models", "pallet.blend"),
                scale=(1.0, 1.0, 1.0),
                physics_enabled=True,
                metadata={
                    "type": "euro_pallet",
                    "dimensions": "1200x800mm",
                    "material": "wood"
                }
            ),
        ]
        
        for asset in default_assets:
            self.asset_registry[asset.asset_id] = asset
            logger.info(f"Registered asset: {asset.name} ({asset.asset_id})")

    def register_asset(self, asset: Asset3D) -> bool:
        """
        Register a new asset in the inventory.
        
        Args:
            asset: Asset3D object to register
            
        Returns:
            Success status
        """
        if asset.asset_id in self.asset_registry:
            logger.warning(f"Asset with ID '{asset.asset_id}' already exists")
            return False
        
        self.asset_registry[asset.asset_id] = asset
        logger.info(f"Registered asset: {asset.name}")
        return True

    def get_asset(self, asset_id: str) -> Optional[Asset3D]:
        """
        Retrieve an asset by ID.
        
        Args:
            asset_id: Asset identifier
            
        Returns:
            Asset3D object or None
        """
        return self.asset_registry.get(asset_id)

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset3D]:
        """
        Get all assets of a specific type.
        
        Args:
            asset_type: Type of asset to filter
            
        Returns:
            List of matching assets
        """
        return [asset for asset in self.asset_registry.values() 
                if asset.asset_type == asset_type]

    def update_asset(self, asset_id: str, **kwargs) -> bool:
        """
        Update asset properties.
        
        Args:
            asset_id: Asset to update
            **kwargs: Properties to update
            
        Returns:
            Success status
        """
        if asset_id not in self.asset_registry:
            logger.error(f"Asset not found: {asset_id}")
            return False
        
        asset = self.asset_registry[asset_id]
        
        # Update allowed fields
        allowed_fields = {'scale', 'position', 'rotation', 'material_name', 'metadata'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(asset, key, value)
        
        logger.info(f"Updated asset: {asset_id}")
        return True

    def create_scene(self, scene_name: str, scene_id: str,
                    description: str = "") -> WarehouseScene:
        """
        Create a new warehouse scene.
        
        Args:
            scene_name: Name of the scene
            scene_id: Unique scene identifier
            description: Scene description
            
        Returns:
            WarehouseScene object
        """
        if scene_id in self.scenes:
            logger.warning(f"Scene with ID '{scene_id}' already exists")
            return self.scenes[scene_id]
        
        scene = WarehouseScene(
            scene_name=scene_name,
            scene_id=scene_id,
            description=description,
            assets=[],
            lighting_config={
                'ambient_strength': 0.5,
                'sun_direction': (1, 1, 1),
                'sun_strength': 1.5
            },
            camera_config={
                'location': (10, 10, 5),
                'rotation': (1.1, 0, 0.785)
            }
        )
        
        self.scenes[scene_id] = scene
        logger.info(f"Created scene: {scene_name}")
        return scene

    def add_asset_to_scene(self, scene_id: str, asset_id: str,
                          position: Optional[Tuple[float, float, float]] = None,
                          rotation: Optional[Tuple[float, float, float]] = None,
                          scale: Optional[Tuple[float, float, float]] = None) -> bool:
        """
        Add an asset to a scene.
        
        Args:
            scene_id: Scene to add to
            asset_id: Asset to add
            position: Position override
            rotation: Rotation override
            scale: Scale override
            
        Returns:
            Success status
        """
        if scene_id not in self.scenes:
            logger.error(f"Scene not found: {scene_id}")
            return False
        
        if asset_id not in self.asset_registry:
            logger.error(f"Asset not found: {asset_id}")
            return False
        
        asset = self.asset_registry[asset_id]
        
        # Create copy with custom properties
        scene_asset = Asset3D(
            asset_id=asset.asset_id,
            name=asset.name,
            asset_type=asset.asset_type,
            model_path=asset.model_path,
            scale=scale or asset.scale,
            position=position or asset.position,
            rotation=rotation or asset.rotation,
            texture_path=asset.texture_path,
            material_name=asset.material_name,
            physics_enabled=asset.physics_enabled,
            animation_path=asset.animation_path,
            metadata=asset.metadata.copy() if asset.metadata else {}
        )
        
        self.scenes[scene_id].assets.append(scene_asset)
        logger.info(f"Added {asset.name} to scene {scene_id}")
        return True

    def remove_asset_from_scene(self, scene_id: str, asset_id: str) -> bool:
        """
        Remove an asset from a scene.
        
        Args:
            scene_id: Scene to remove from
            asset_id: Asset to remove
            
        Returns:
            Success status
        """
        if scene_id not in self.scenes:
            logger.error(f"Scene not found: {scene_id}")
            return False
        
        scene = self.scenes[scene_id]
        initial_count = len(scene.assets)
        scene.assets = [a for a in scene.assets if a.asset_id != asset_id]
        
        if len(scene.assets) < initial_count:
            logger.info(f"Removed asset {asset_id} from scene {scene_id}")
            return True
        else:
            logger.warning(f"Asset {asset_id} not found in scene {scene_id}")
            return False

    def get_scene(self, scene_id: str) -> Optional[WarehouseScene]:
        """
        Get a scene by ID.
        
        Args:
            scene_id: Scene identifier
            
        Returns:
            WarehouseScene or None
        """
        return self.scenes.get(scene_id)

    def export_scene_config(self, scene_id: str, output_path: str) -> bool:
        """
        Export scene configuration as JSON for Blender.
        
        Args:
            scene_id: Scene to export
            output_path: Path to save JSON config
            
        Returns:
            Success status
        """
        if scene_id not in self.scenes:
            logger.error(f"Scene not found: {scene_id}")
            return False
        
        scene = self.scenes[scene_id]
        
        config = {
            'scene_name': scene.scene_name,
            'scene_id': scene.scene_id,
            'description': scene.description,
            'duration': scene.duration,
            'frame_rate': scene.frame_rate,
            'resolution': scene.resolution,
            'lighting': scene.lighting_config,
            'camera': scene.camera_config,
            'assets': [asset.to_dict() for asset in scene.assets]
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Exported scene config: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error exporting scene: {e}")
            return False

    def generate_blender_setup_script(self, scene_id: str, output_script: str) -> bool:
        """
        Generate Blender Python script to set up scene.
        
        Args:
            scene_id: Scene to generate script for
            output_script: Path to save script
            
        Returns:
            Success status
        """
        if scene_id not in self.scenes:
            logger.error(f"Scene not found: {scene_id}")
            return False
        
        scene = self.scenes[scene_id]
        
        script = f'''#!/usr/bin/env python3
import bpy
import json
import os

# Scene setup for: {scene.scene_name}

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create world/scene properties
scene = bpy.context.scene
scene.name = "{scene.scene_name}"
scene.render.fps = {scene.frame_rate}
scene.render.resolution_x = {scene.resolution[0]}
scene.render.resolution_y = {scene.resolution[1]}

# Setup lighting
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_data.energy = {scene.lighting_config.get('sun_strength', 1.5)}
sun_object = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_object)
sun_object.location = {tuple(scene.lighting_config.get('sun_direction', (1, 1, 1)))}

# Setup camera
camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
camera_object.location = {tuple(scene.camera_config.get('location', (10, 10, 5)))}
camera_object.rotation_euler = {tuple(scene.camera_config.get('rotation', (1.1, 0, 0.785)))}
scene.camera = camera_object

# Assets configuration
assets_to_load = [
'''
        
        for asset in scene.assets:
            script += f'''    {{
        'name': '{asset.name}',
        'type': '{asset.asset_type.value}',
        'path': '{asset.model_path}',
        'location': {asset.position},
        'rotation': {asset.rotation},
        'scale': {asset.scale},
    }},
'''
        
        script += f'''
]

# Load and position assets
for asset_config in assets_to_load:
    try:
        # Import asset (append from .blend file)
        with bpy.data.libraries.load(asset_config['path'], link=False) as (data_from, data_to):
            data_to.objects = data_from.objects
        
        # Place object
        obj = data_to.objects[0]
        bpy.context.collection.objects.link(obj)
        obj.location = asset_config['location']
        obj.rotation_euler = asset_config['rotation']
        obj.scale = asset_config['scale']
        
        print(f"Loaded: {{asset_config['name']}}")
    except Exception as e:
        print(f"Error loading {{asset_config['name']}}: {{e}}")

print("Warehouse scene setup complete!")
bpy.ops.wm.save_mainfile()
'''
        
        try:
            with open(output_script, 'w') as f:
                f.write(script)
            logger.info(f"Generated Blender setup script: {output_script}")
            return True
        except Exception as e:
            logger.error(f"Error generating script: {e}")
            return False

    def list_all_assets(self) -> List[Dict]:
        """
        List all registered assets.
        
        Returns:
            List of asset dictionaries
        """
        return [asset.to_dict() for asset in self.asset_registry.values()]

    def list_all_scenes(self) -> List[Dict]:
        """
        List all scenes.
        
        Returns:
            List of scene summaries
        """
        return [
            {
                'scene_id': scene.scene_id,
                'scene_name': scene.scene_name,
                'asset_count': len(scene.assets),
                'duration': scene.duration
            }
            for scene in self.scenes.values()
        ]

    def get_asset_statistics(self) -> Dict:
        """
        Get statistics about asset inventory.
        
        Returns:
            Dictionary with asset statistics
        """
        stats = {
            'total_assets': len(self.asset_registry),
            'by_type': {}
        }
        
        for asset_type in AssetType:
            count = len(self.get_assets_by_type(asset_type))
            if count > 0:
                stats['by_type'][asset_type.value] = count
        
        return stats
