import os
from dotenv import load_dotenv
import google.generativeai as genai

# Explicitly load .env from the same directory as this script
from pathlib import Path
script_dir = Path(__file__).parent
env_path = script_dir / '.env'
print(f"DEBUG: Loading .env from {env_path}")
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

print(f"DEBUG: Loaded API Key (first 10 chars): {api_key[:10] if api_key else 'None'}...")
print(f"DEBUG: Loaded API Key (last 5 chars): ...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("ERROR: No API Key found in environment variables!")
    exit(1)

genai.configure(api_key=api_key)

try:
    print("DEBUG: Attempting to list available models...")
    # List models to check connection
    models = [m.name for m in genai.list_models()]
    print(f"SUCCESS: Connected to Gemini API! Found {len(models)} models.")
    print("Available (top 5):", models[:5])

    print("\nDEBUG: Attempting a simple generation...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working?")
    print(f"SUCCESS: Generation received!\nResponse: {response.text}")

except Exception as e:
    print("\nCRITICAL FAILURE:")
    print(f"Type: {type(e).__name__}")
    print(f"Message: {str(e)}")
