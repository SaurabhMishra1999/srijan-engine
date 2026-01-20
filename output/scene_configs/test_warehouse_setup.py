#!/usr/bin/env python3
import bpy
import json
import os

# Scene setup for: Test Warehouse

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create world/scene properties
scene = bpy.context.scene
scene.name = "Test Warehouse"
scene.render.fps = 30
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

# Setup lighting
sun_data = bpy.data.lights.new(name="Sun", type='SUN')
sun_data.energy = 1.5
sun_object = bpy.data.objects.new("Sun", sun_data)
bpy.context.collection.objects.link(sun_object)
sun_object.location = (1, 1, 1)

# Setup camera
camera_data = bpy.data.cameras.new(name="Camera")
camera_object = bpy.data.objects.new("Camera", camera_data)
bpy.context.collection.objects.link(camera_object)
camera_object.location = (10, 10, 5)
camera_object.rotation_euler = (1.1, 0, 0.785)
scene.camera = camera_object

# Assets configuration
assets_to_load = [
    {
        'name': 'Standard Forklift',
        'type': 'forklift',
        'path': 'E:\Srijan_Engine\assets\models\models\forklift.blend',
        'location': (0, 0, 0),
        'rotation': (0.0, 0.0, 0.0),
        'scale': (1.0, 1.0, 1.0),
    },
    {
        'name': 'Container Truck',
        'type': 'container_truck',
        'path': 'E:\Srijan_Engine\assets\models\models\container_truck.blend',
        'location': (5, 0, 0),
        'rotation': (0.0, 0.0, 0.0),
        'scale': (1.0, 1.0, 1.0),
    },

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
        
        print(f"Loaded: {asset_config['name']}")
    except Exception as e:
        print(f"Error loading {asset_config['name']}: {e}")

print("Warehouse scene setup complete!")
bpy.ops.wm.save_mainfile()
