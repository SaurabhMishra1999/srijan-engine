"""
Scene Configuration API Endpoints
Provides REST API for scene management and configuration
"""

from flask import Flask, request, jsonify
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.blender.scene_manager import (
    SceneSetupManager, SceneConfig, SceneObject, Camera, LightSource
)

class SceneConfigAPI:
    """Manages scene configuration API endpoints"""
    
    def __init__(self, app: Flask):
        """Initialize scene config API"""
        self.app = app
        self.manager = SceneSetupManager()
        self._register_routes()
    
    def _register_routes(self):
        """Register all scene configuration routes"""
        
        @self.app.route('/api/scenes', methods=['GET'])
        def list_all_scenes():
            """List all created scenes"""
            scenes = self.manager.get_all_scenes()
            result = {
                'count': len(scenes),
                'scenes': [
                    self.manager.get_scene_info(name)
                    for name in scenes.keys()
                ]
            }
            return jsonify(result), 200
        
        @self.app.route('/api/scenes/<scene_name>', methods=['GET'])
        def get_scene_details(scene_name):
            """Get detailed scene information"""
            info = self.manager.get_scene_info(scene_name)
            if not info:
                return jsonify({'error': 'Scene not found'}), 404
            
            scene = self.manager.get_scene(scene_name)
            return jsonify({
                'info': info,
                'objects': [
                    {
                        'name': obj.name,
                        'type': obj.type,
                        'position': obj.position,
                        'rotation': obj.rotation,
                        'scale': obj.scale,
                        'color': obj.color,
                        'material': obj.material
                    }
                    for obj in scene.objects
                ] if scene else [],
                'lights': [
                    {
                        'name': light.name,
                        'type': light.type,
                        'position': light.position,
                        'energy': light.energy,
                        'color': light.color
                    }
                    for light in scene.lights
                ] if scene else []
            }), 200
        
        @self.app.route('/api/scenes', methods=['POST'])
        def create_scene():
            """Create a new scene"""
            data = request.get_json()
            
            name = data.get('name')
            description = data.get('description', 'Custom scene')
            duration = data.get('duration', 5.0)
            template = data.get('template', None)  # Can be None or template name
            
            if not name:
                return jsonify({'error': 'Scene name is required'}), 400
            
            try:
                scene = self.manager.create_custom_scene(
                    name=name,
                    description=description,
                    duration=duration,
                    template=template
                )
                
                return jsonify({
                    'success': True,
                    'message': f'Scene "{name}" created successfully',
                    'scene': self.manager.get_scene_info(name)
                }), 201
            
            except Exception as e:
                return jsonify({'error': str(e)}), 400
        
        @self.app.route('/api/scenes/<scene_name>', methods=['PUT'])
        def update_scene(scene_name):
            """Update scene properties"""
            data = request.get_json()
            scene = self.manager.get_scene(scene_name)
            
            if not scene:
                return jsonify({'error': 'Scene not found'}), 404
            
            # Update basic properties
            if 'description' in data:
                scene.description = data['description']
            if 'duration' in data:
                scene.duration = data['duration']
            if 'background_color' in data:
                scene.background_color = tuple(data['background_color'])
            if 'ambient_light_strength' in data:
                scene.ambient_light_strength = data['ambient_light_strength']
            
            return jsonify({
                'success': True,
                'message': 'Scene updated',
                'scene': self.manager.get_scene_info(scene_name)
            }), 200
        
        @self.app.route('/api/scenes/<scene_name>', methods=['DELETE'])
        def delete_scene(scene_name):
            """Delete a scene"""
            if self.manager.delete_scene(scene_name):
                return jsonify({
                    'success': True,
                    'message': f'Scene "{scene_name}" deleted'
                }), 200
            else:
                return jsonify({'error': 'Scene not found'}), 404
        
        @self.app.route('/api/scenes/<scene_name>/clone', methods=['POST'])
        def clone_scene(scene_name):
            """Clone an existing scene"""
            data = request.get_json()
            new_name = data.get('new_name')
            
            if not new_name:
                return jsonify({'error': 'new_name is required'}), 400
            
            if self.manager.clone_scene(scene_name, new_name):
                return jsonify({
                    'success': True,
                    'message': f'Scene cloned to "{new_name}"',
                    'scene': self.manager.get_scene_info(new_name)
                }), 201
            else:
                return jsonify({'error': 'Source scene not found'}), 404
        
        # Lighting endpoints
        @self.app.route('/api/lighting-presets', methods=['GET'])
        def list_lighting_presets():
            """List available lighting presets"""
            return jsonify({
                'presets': self.manager.list_lighting_presets()
            }), 200
        
        @self.app.route('/api/scenes/<scene_name>/lighting', methods=['POST'])
        def apply_lighting(scene_name):
            """Apply a lighting preset to scene"""
            data = request.get_json()
            preset = data.get('preset')
            
            if not preset:
                return jsonify({'error': 'preset is required'}), 400
            
            if self.manager.apply_lighting_preset(scene_name, preset):
                return jsonify({
                    'success': True,
                    'message': f'Applied lighting preset "{preset}"',
                    'scene': self.manager.get_scene_info(scene_name)
                }), 200
            else:
                return jsonify({'error': 'Scene or preset not found'}), 404
        
        # Color grading endpoints
        @self.app.route('/api/color-grading-presets', methods=['GET'])
        def list_color_presets():
            """List available color grading presets"""
            return jsonify({
                'presets': self.manager.list_color_grading_presets()
            }), 200
        
        @self.app.route('/api/scenes/<scene_name>/color-grading', methods=['POST'])
        def apply_color_grading(scene_name):
            """Apply a color grading preset"""
            data = request.get_json()
            preset = data.get('preset')
            
            if not preset:
                return jsonify({'error': 'preset is required'}), 400
            
            if self.manager.apply_color_grading_preset(scene_name, preset):
                return jsonify({
                    'success': True,
                    'message': f'Applied color grading "{preset}"',
                    'scene': self.manager.get_scene_info(scene_name)
                }), 200
            else:
                return jsonify({'error': 'Scene or preset not found'}), 404
        
        # Object management
        @self.app.route('/api/scenes/<scene_name>/objects', methods=['POST'])
        def add_object(scene_name):
            """Add an object to a scene"""
            data = request.get_json()
            
            obj = SceneObject(
                name=data.get('name', 'Object'),
                type=data.get('type', 'prop'),
                position=tuple(data.get('position', (0, 0, 0))),
                rotation=tuple(data.get('rotation', (0, 0, 0))),
                scale=tuple(data.get('scale', (1, 1, 1))),
                color=data.get('color'),
                material=data.get('material')
            )
            
            if self.manager.add_object_to_scene(scene_name, obj):
                return jsonify({
                    'success': True,
                    'message': f'Object "{obj.name}" added',
                    'object': {
                        'name': obj.name,
                        'type': obj.type,
                        'position': obj.position
                    }
                }), 201
            else:
                return jsonify({'error': 'Scene not found'}), 404
        
        # Light management
        @self.app.route('/api/scenes/<scene_name>/lights', methods=['POST'])
        def add_light(scene_name):
            """Add a light to a scene"""
            data = request.get_json()
            
            light = LightSource(
                name=data.get('name', 'Light'),
                type=data.get('type', 'SUN'),
                position=tuple(data.get('position', (0, 0, 10))),
                energy=data.get('energy', 2.0),
                color=tuple(data.get('color', (1.0, 1.0, 1.0))),
                intensity=data.get('intensity', 1.0)
            )
            
            if self.manager.add_light_to_scene(scene_name, light):
                return jsonify({
                    'success': True,
                    'message': f'Light "{light.name}" added',
                    'light': {
                        'name': light.name,
                        'type': light.type,
                        'energy': light.energy
                    }
                }), 201
            else:
                return jsonify({'error': 'Scene not found'}), 404
        
        # Camera management
        @self.app.route('/api/scenes/<scene_name>/camera', methods=['POST'])
        def set_camera(scene_name):
            """Configure scene camera"""
            data = request.get_json()
            
            camera = Camera(
                name=data.get('name', 'Camera'),
                position=tuple(data.get('position', (0, -10, 5))),
                rotation=tuple(data.get('rotation', (0, 0, 0))),
                focal_length=data.get('focal_length', 50.0),
                fov=data.get('fov', 50.0)
            )
            
            if self.manager.configure_camera(scene_name, camera):
                return jsonify({
                    'success': True,
                    'message': 'Camera configured',
                    'camera': {
                        'name': camera.name,
                        'position': camera.position,
                        'fov': camera.fov
                    }
                }), 200
            else:
                return jsonify({'error': 'Scene not found'}), 404
        
        # Templates
        @self.app.route('/api/templates', methods=['GET'])
        def list_templates():
            """List available scene templates"""
            return jsonify({
                'templates': self.manager.list_templates(),
                'count': len(self.manager.list_templates())
            }), 200
        
        # Export/Import
        @self.app.route('/api/scenes/<scene_name>/export', methods=['GET'])
        def export_scene(scene_name):
            """Export scene as JSON"""
            output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'output'
            )
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f'{scene_name}_config.json')
            
            if self.manager.export_scene(scene_name, output_path):
                return jsonify({
                    'success': True,
                    'message': f'Scene exported',
                    'path': output_path
                }), 200
            else:
                return jsonify({'error': 'Export failed'}), 500
        
        @self.app.route('/api/scenes/import', methods=['POST'])
        def import_scene():
            """Import scene from JSON"""
            data = request.get_json()
            json_path = data.get('path')
            scene_name = data.get('name')
            
            if not json_path or not os.path.exists(json_path):
                return jsonify({'error': 'File not found'}), 404
            
            if self.manager.import_scene(json_path, scene_name):
                return jsonify({
                    'success': True,
                    'message': 'Scene imported'
                }), 201
            else:
                return jsonify({'error': 'Import failed'}), 500


# Usage in main web app:
# from src.blender.scene_config_api import SceneConfigAPI
# 
# api = SceneConfigAPI(app)
