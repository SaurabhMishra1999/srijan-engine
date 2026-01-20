# 🎬 Scene Configuration System - Complete Guide

## Overview

Srijan Engine ab **warehouse-specific setup ko remove karke** ek **fully flexible, dynamic scene configuration system** provide karta hai jo:

✅ **Koi bhi scene setup kar sakte ho** (warehouse, office, studio, outdoor, etc.)  
✅ **Unlimited templates** aur presets  
✅ **Full customization** - lights, objects, camera, effects  
✅ **Live editing** - real-time scene modification  
✅ **Export/Import** - scenes save aur share karne ka option  

---

## Features

### 1. **Scene Management** 
- Create unlimited custom scenes
- Clone existing scenes
- Delete scenes
- Export/Import as JSON

### 2. **Lighting System**
- 4 pre-built lighting presets:
  - **Soft** - Gentle, diffused lighting
  - **Dramatic** - High contrast, moody
  - **Natural** - Daylight simulation
  - **Cinematic** - Professional film lighting
- Add custom lights (Sun, Point, Area, Spot)
- Adjust energy, color, position for each light
- Full control over ambient light strength

### 3. **Color Grading**
- 6 pre-built color presets:
  - **Neutral** - Standard colors
  - **Warm** - Golden, sunset tones
  - **Cool** - Blue, cold tones
  - **Cinematic** - Professional look
  - **Vintage** - Retro film style
  - **Noir** - Black & white dramatic

### 4. **Object Management**
- Add props, characters, environments
- Position objects in 3D space (X, Y, Z)
- Scale and rotate objects
- Apply colors and materials
- Animation support

### 5. **Camera Control**
- Position camera anywhere in 3D space
- Adjust FOV (Field of View)
- Focal length configuration
- Look-at targeting

### 6. **Scene Templates**
Instant scene setup - choose a template to start:
- **Empty** - Blank canvas
- **Office** - Modern office setup
- **Studio** - Professional studio
- **Outdoor** - Natural outdoor environment
- **Dark Dramatic** - Moody, dramatic scene

---

## Getting Started

### Option 1: Web Interface (Recommended)

```bash
python web_app.py
```

Then visit: **http://localhost:5000/scene-editor**

**Steps:**
1. Click "Create New Scene"
2. Enter scene name (e.g., "My Warehouse", "Office Setup")
3. Choose a template (optional) or leave empty
4. Click "Create Scene"
5. Select scene from list
6. Use tabs to customize:
   - **Settings** - Basic scene properties
   - **Lighting** - Add lights, apply presets
   - **Objects** - Add props, characters
   - **Camera** - Position and configure camera

### Option 2: Python API

```python
from src.blender.scene_manager import SceneSetupManager

manager = SceneSetupManager()

# Create custom scene
manager.create_custom_scene(
    name="My Scene",
    description="Custom scene description",
    duration=10,
    template="office"  # optional
)

# Apply presets
manager.apply_lighting_preset("My Scene", "cinematic")
manager.apply_color_grading_preset("My Scene", "warm")

# Customize scene
from src.blender.scene_manager import SceneObject, LightSource

# Add object
obj = SceneObject(
    name="Desk",
    type="prop",
    position=(0, 0, 0),
    color="#8B4513"
)
manager.add_object_to_scene("My Scene", obj)

# Add light
light = LightSource(
    name="Key Light",
    type="AREA",
    position=(-3, -5, 4),
    energy=2.0
)
manager.add_light_to_scene("My Scene", light)

# Save
manager.export_scene("My Scene", "scenes/my_scene.json")
```

### Option 3: REST API

```bash
# Create scene
curl -X POST http://localhost:5000/api/scenes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Scene",
    "description": "Beautiful scene",
    "duration": 10,
    "template": "studio"
  }'

# List all scenes
curl http://localhost:5000/api/scenes

# Apply lighting preset
curl -X POST http://localhost:5000/api/scenes/My Scene/lighting \
  -H "Content-Type: application/json" \
  -d '{"preset": "cinematic"}'

# Add light to scene
curl -X POST http://localhost:5000/api/scenes/My Scene/lights \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fill Light",
    "type": "AREA",
    "position": [3, -5, 3],
    "energy": 1.5
  }'

# Add object
curl -X POST http://localhost:5000/api/scenes/My Scene/objects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chair",
    "type": "prop",
    "position": [0, -1, 0],
    "color": "#333333"
  }'

# Configure camera
curl -X POST http://localhost:5000/api/scenes/My Scene/camera \
  -H "Content-Type: application/json" \
  -d '{
    "position": [0, -10, 5],
    "fov": 50,
    "focal_length": 50
  }'

# Export scene
curl http://localhost:5000/api/scenes/My Scene/export

# Delete scene
curl -X DELETE http://localhost:5000/api/scenes/My Scene
```

---

## Available Templates

### Office Template
- Desk, chair, monitor, lamp
- Professional lighting
- Light background color
- Best for: Corporate, education scenes

### Studio Template
- No objects (ready for custom setup)
- Professional 3-light setup
- Neutral gray background
- Best for: Product shots, interviews

### Outdoor Template
- Ground and sky objects
- Natural sunlight simulation
- Blue sky background
- Best for: Outdoor scenes, nature

### Dark Dramatic Template
- No objects
- Dramatic spot and fill lighting
- Very dark background
- Bloom effects enabled
- Best for: Suspense, drama, moody scenes

### Empty Template
- Blank canvas
- Basic single light
- Default settings
- Best for: Starting from scratch

---

## Lighting Presets Explained

### Soft Lighting
```
Key Light: AREA, 70% energy
Fill Light: AREA, 50% energy
High ambient light (70%)
= Gentle, flattering light
```

### Dramatic Lighting
```
Key Light: SPOT, 100% energy (sharp)
Fill Light: POINT, 20% energy
Low ambient light (30%)
= High contrast, shadows
```

### Natural Lighting
```
Sun Light: SUN, 100% energy (warm)
Sky Light: SUN, 30% energy (cool)
Medium ambient light (60%)
= Realistic daylight
```

### Cinematic Lighting
```
Key Light: AREA, 80% energy (warm)
Fill Light: AREA, 40% energy (cool)
Back Light: POINT, 30% energy
Medium ambient light (40%)
= Professional film look
```

---

## Color Grading Presets

| Preset | Use Case |
|--------|----------|
| **Neutral** | Standard, unmodified colors |
| **Warm** | Sunsets, cozy, nostalgic feelings |
| **Cool** | Modern, futuristic, cold atmosphere |
| **Cinematic** | Professional, high-contrast look |
| **Vintage** | Retro, film stock appearance |
| **Noir** | Black & white, dramatic mood |

---

## Scene Configuration Tips

### For Product Shots
```
Template: Studio
Lighting: Cinematic
Color Grading: Neutral or Warm
Camera FOV: 50-60
Objects: Your product
```

### For Interviews
```
Template: Studio
Lighting: Soft
Color Grading: Cinematic
Camera FOV: 50
Objects: Chair
Lights: 3-light setup
```

### For Dramatic Story
```
Template: Dark Dramatic
Lighting: Dramatic
Color Grading: Noir
Camera FOV: 40-50
Objects: Props for story
```

### For Outdoor Scene
```
Template: Outdoor
Lighting: Natural
Color Grading: Warm or Neutral
Camera FOV: 50-70
Sky: Use environment
```

---

## Complete Example: Custom Office Scene

```python
from src.blender.scene_manager import (
    SceneSetupManager, SceneObject, LightSource, Camera
)

manager = SceneSetupManager()

# Create scene from template
manager.create_custom_scene(
    name="Modern Office",
    description="A sleek modern office workspace",
    duration=15,
    template="office"
)

# Customize scene
manager.apply_lighting_preset("Modern Office", "cinematic")
manager.apply_color_grading_preset("Modern Office", "cool")

# Add more objects
manager.add_object_to_scene("Modern Office", SceneObject(
    name="Laptop",
    type="prop",
    position=(0.5, 0, 1),
    color="#333333"
))

manager.add_object_to_scene("Modern Office", SceneObject(
    name="Coffee Cup",
    type="prop",
    position=(0.2, 0.2, 0.8),
    color="#8B4513"
))

# Add accent light
manager.add_light_to_scene("Modern Office", LightSource(
    name="Accent Light",
    type="SPOT",
    position=(5, 5, 3),
    energy=0.8,
    color=(0.5, 0.8, 1.0)  # Cool blue
))

# Configure camera
manager.configure_camera("Modern Office", Camera(
    name="Main Camera",
    position=(0, -8, 2),
    fov=45
))

# Export for later use
manager.export_scene("Modern Office", "scenes/office.json")

# Print summary
manager.print_scene_summary("Modern Office")
```

**Output:**
```
============================================================
SCENE: Modern Office
============================================================
Description: A sleek modern office workspace
Duration: 15.0 seconds
Resolution: 1920x1080
Objects: 3
Lights: 4
Render Engine: EEVEE
Camera: Yes
Background Color: (0.95, 0.95, 0.95)
Color Grading: {'temp': -0.3, 'saturation': 1.0, 'contrast': 1.0}
============================================================
```

---

## Web UI Navigation

### Scene Editor Interface

**Left Panel:**
- Scene creation form
- Scene list (click to select)

**Right Panel:**
- Scene editor with 4 tabs:
  1. **Settings** - Duration, description, background color
  2. **Lighting** - Lighting presets, add custom lights
  3. **Objects** - Object list, add props/characters
  4. **Camera** - Position, FOV, focal length

**Bottom Section:**
- Scene info display
- Export, delete, clone buttons

---

## API Endpoints Reference

```
GET    /api/scenes                          - List all scenes
POST   /api/scenes                          - Create scene
GET    /api/scenes/<name>                   - Get scene details
PUT    /api/scenes/<name>                   - Update scene
DELETE /api/scenes/<name>                   - Delete scene
POST   /api/scenes/<name>/clone             - Clone scene

POST   /api/scenes/<name>/lighting          - Apply lighting preset
POST   /api/scenes/<name>/color-grading     - Apply color grading

POST   /api/scenes/<name>/lights            - Add light
POST   /api/scenes/<name>/objects           - Add object
POST   /api/scenes/<name>/camera            - Configure camera

GET    /api/templates                       - List templates
GET    /api/lighting-presets               - List lighting presets
GET    /api/color-grading-presets          - List color presets

GET    /api/scenes/<name>/export            - Export as JSON
POST   /api/scenes/import                   - Import from JSON
```

---

## Best Practices

1. **Start with a Template** - Don't start from scratch, choose a template
2. **Apply Presets** - Use lighting/color presets before fine-tuning
3. **Save Often** - Export scenes regularly to avoid losing changes
4. **Use Meaningful Names** - Name scenes and objects clearly
5. **Test Different Cameras** - Try different FOV and positions
6. **Layer Lights** - Use multiple lights for professional look
7. **Organize Objects** - Group related objects together

---

## Troubleshooting

### Scene not saving
- Make sure `output/` folder exists
- Check file permissions
- Try exporting instead

### Changes not visible
- Refresh the web page (Ctrl+R)
- Reload scene list
- Check browser console for errors

### API errors
- Verify scene name spelling
- Check JSON syntax in request
- Review server logs

---

## Summary

**Warehouse-specific setup removed** ✅  
**Universal scene configuration system added** ✅  
**5 templates + 4 lighting presets + 6 color presets** ✅  
**Full REST API** ✅  
**Web UI for easy editing** ✅  

अब आप **किसी भी प्रकार का scene बना सकते हैं!** 🎬

---

**Start here:** http://localhost:5000/scene-editor
