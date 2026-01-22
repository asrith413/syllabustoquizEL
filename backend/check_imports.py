import sys
import os
print(f"Python: {sys.version}")
print("Checking imports...")

try:
    import torch
    print(f"Torch: {torch.__version__}")
except ImportError as e:
    print(f"Torch not found: {e}")
except Exception as e:
    print(f"Torch import error: {e}")

try:
    import easyocr
    print(f"EasyOCR: {easyocr.__version__}")
except ImportError as e:
    print(f"EasyOCR not found: {e}")
except Exception as e:
    print(f"EasyOCR import error: {e}")

try:
    import cv2
    print(f"OpenCV: {cv2.__version__}")
except ImportError as e:
    print(f"OpenCV not found: {e}")

try:
    import google.generativeai as genai
    print(f"Google GenAI: {genai.__version__}")
except ImportError as e:
    print(f"Google GenAI not found: {e}")

try:
    import grpc
    print(f"gRPC: {grpc.__version__}")
except ImportError as e:
    print(f"gRPC not found: {e}")
