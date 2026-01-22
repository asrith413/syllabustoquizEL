import google.generativeai as genai
import os
from pathlib import Path
from dotenv import load_dotenv

script_dir = Path(__file__).parent
env_path = script_dir / '.env'
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY")

print("Configuring with transport='rest'...")
genai.configure(api_key=api_key, transport='rest')

try:
    print("Listing models...")
    # This should use HTTP, not gRPC
    for m in genai.list_models():
        print(f" - {m.name}")
        break  # Just need one to prove connection
    
    print("\nGenerating content...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello")
    print(f"Response: {response.text}")
    print("SUCCESS: Full cycle completed with transport='rest'")

except Exception as e:
    print(f"\nFAILURE: {e}")
    import traceback
    traceback.print_exc()

# Inspect internal client if possible (hacky)
try:
    client = genai.get_model('models/gemini-1.5-flash')._client
    print(f"\nInternal Client Type: {type(client)}")
except:
    pass
