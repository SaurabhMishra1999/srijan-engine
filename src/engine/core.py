import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get the API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in a .env file.")

genai.configure(api_key=api_key)

def check_hardware_compatibility():
    """
    Check system compatibility for Blender rendering.
    """
    import platform
    import psutil
    system = platform.system()
    cpu_count = psutil.cpu_count()
    ram = psutil.virtual_memory().total / (1024**3)  # GB
    print(f"System: {system}, CPUs: {cpu_count}, RAM: {ram:.1f}GB")
    if ram < 8:
        print("Warning: Low RAM detected. Rendering may be slow.")
    # Check for GPU if possible
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            print(f"GPU detected: {gpus[0].name}")
        else:
            print("No GPU detected, using CPU.")
    except ImportError:
        print("GPUtil not installed, skipping GPU check.")
    return True

def generate_blender_code(script):
    """
    Main function to convert movie script to Blender Python (bpy) commands using Gemini API.
    """
    prompt = f"""You are a Blender Python expert. Convert the following scene into bpy code for Eevee engine. Include:
- Scene setup
- Camera placement
- Lighting
- Basic objects
- Eevee render settings
Return ONLY the code.

Scene: {script}"""

    model = genai.GenerativeModel('gemini-1.5-pro')
    response = model.generate_content(prompt)
    bpy_code = response.text.strip()
    return bpy_code