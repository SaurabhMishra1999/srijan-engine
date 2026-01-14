import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables. Please set it in a .env file.")

genai.configure(api_key=api_key)

def process_script(script):
    """
    Converts the user's movie script into Blender Python (bpy) code using Gemini 1.5 Pro.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = "You are a Blender Python expert. Convert the following scene into bpy code for Eevee engine. Return ONLY the code.\n\nScene: " + script
    response = model.generate_content(prompt)
    bpy_code = response.text.strip()
    return bpy_code