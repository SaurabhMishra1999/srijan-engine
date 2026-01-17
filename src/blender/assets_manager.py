import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)

# Asset directories
ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets')
ENVIRONMENTS_DIR = os.path.join(ASSETS_DIR, 'environments')
MODELS_DIR = os.path.join(ASSETS_DIR, 'models')

def get_available_environments():
    """Get list of available environment names."""
    if not os.path.exists(ENVIRONMENTS_DIR):
        os.makedirs(ENVIRONMENTS_DIR, exist_ok=True)
        # Create placeholder files
        for env in ['Temple', 'Forest', 'Modern Room']:
            with open(os.path.join(ENVIRONMENTS_DIR, f'{env}.blend'), 'w') as f:
                f.write("# Placeholder for " + env)
    return ['Temple', 'Forest', 'Modern Room']

def get_available_characters():
    """Get list of available character names."""
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR, exist_ok=True)
        # Create placeholder files
        for char in ['Monk', 'Devotee']:
            with open(os.path.join(MODELS_DIR, f'{char}.obj'), 'w') as f:
                f.write("# Placeholder for " + char)
    return ['Basic Head', 'Monk', 'Devotee']

def load_environment(env_name):
    """Generate bpy code to load environment."""
    env_path = os.path.join(ENVIRONMENTS_DIR, f'{env_name}.blend')
    code = f"""
# Load Environment
import bpy
with bpy.data.libraries.load('{env_path}', link=False) as (data_from, data_to):
    data_to.scenes = data_from.scenes
    data_to.objects = data_from.objects
# Add loaded objects to scene
for obj in data_to.objects:
    if obj is not None:
        bpy.context.collection.objects.link(obj)
"""
    return code

def load_character(char_name):
    """Generate bpy code to load character model."""
    char_path = os.path.join(MODELS_DIR, f'{char_name}.obj')
    code = f"""
# Load Character
import bpy
bpy.ops.import_scene.obj(filepath='{char_path}')
head = bpy.context.selected_objects[0]
head.name = 'Head'
head.location = (0, 0, 1.5)
# Assume the model has shape keys or add them
if not head.data.shape_keys:
    bpy.ops.object.shape_key_add(from_mix=False)
    mouth_shape = head.data.shape_keys.key_blocks['Key 1']
    mouth_shape.name = 'mouth_open'
    # For simplicity, assume deformation is already in the model
"""
    return code

def detect_mood(script):
    """Use AI to detect mood from script."""
    if not api_key:
        return 'Neutral'
    prompt = f"Analyze this script and determine the overall mood/emotion. Return only one word: Dark, Bright, Intense, Divine, Neutral, etc.\n\nScript: {script}"
    try:
        response = client.models.generate_content(model='gemini-1.5-pro', contents=prompt)
        mood = response.text.strip().split()[0]  # Take first word
        return mood
    except:
        return 'Neutral'

def get_lighting_for_mood(mood):
    """Generate bpy code for lighting based on mood."""
    lighting_configs = {
        'Dark': """
# Dark/Intense lighting
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object
sun.data.energy = 0.5
sun.data.color = (0.1, 0.1, 0.2)
bpy.ops.object.light_add(type='POINT', location=(2, -2, 2))
point = bpy.context.active_object
point.data.energy = 100
point.data.color = (1, 0.5, 0)  # Orange tint
""",
        'Bright': """
# Bright/Divine lighting
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object
sun.data.energy = 2.0
sun.data.color = (1, 1, 0.9)
bpy.ops.object.light_add(type='AREA', location=(0, -5, 3))
area = bpy.context.active_object
area.data.energy = 500
area.data.color = (1, 1, 1)
""",
        'Neutral': """
# Neutral lighting
bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))
sun = bpy.context.active_object
sun.data.energy = 1.0
sun.data.color = (1, 1, 1)
"""
    }
    return lighting_configs.get(mood, lighting_configs['Neutral'])