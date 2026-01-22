import google.generativeai as genai
import os

print(f"GenAI Version: {genai.__version__}")
try:
    # Just checking signature, not making call
    genai.configure(api_key="TEST_KEY", transport='rest')
    print("SUCCESS: transport='rest' argument accepted.")
except TypeError as e:
    print(f"FAILURE: transport argument not supported: {e}")
except Exception as e:
    print(f"FAILURE: Other error: {e}")
