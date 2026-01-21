import os
import sys
# Add current directory to path so we can import services
sys.path.append(os.getcwd())

from services.ocr_service import OCRService

def test():
    ocr = OCRService()
    
    # 1. Create a dummy test image
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (400, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10,10), "HELLO WORLD TEST", fill=(0,0,0))
        img.save('backend_test_image.png')
        print(f"Created synthetic test image: backend_test_image.png")
        
        print("--- TEST ON SYNTHETIC IMAGE ---")
        res = ocr.extract_text('backend_test_image.png')
        print(f"Synthetic Result: '{res}'")
        if "HELLO" in res:
            print("OCR IS WORKING correctly on synthetic image.")
        else:
            print("OCR FAILED on synthetic image.")
    except Exception as e:
        print(f"Failed to create/test synthetic image: {e}")
        import traceback
        traceback.print_exc()

    # Path to the uploaded file - absolute path
    image_path = os.path.abspath("uploads/Screenshot 2026-01-17 121758.png")
    
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        # Try to find any png file in uploads
        uploads_dir = os.path.join(os.getcwd(), "uploads")
        if os.path.exists(uploads_dir):
            files = [f for f in os.listdir(uploads_dir) if f.endswith('.png')]
            if files:
                image_path = os.path.join(uploads_dir, files[0])
                print(f"Found alternative file: {image_path}")
    
    print(f"Testing image: {image_path}")
    
    # Check if cv2 can read it
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            print("ERROR: cv2.imread returned None!")
        else:
            print(f"SUCCESS: cv2 loaded image. Shape: {img.shape}")
    except Exception as e:
        print(f"ERROR loading cv2: {e}")

    print("--- START OCR (Basic Mode) ---")
    try:
        if ocr.reader:
           # Try raw readtext first
           pass
    except:
        pass

    print("--- START OCR (Service Mode) ---")
    text = ocr.extract_text(image_path)
    print("--- RAW TEXT ---")
    print(text)
    
    print("--- EXTRACT TOPICS ---")
    topics = ocr.extract_topics(text)
    print(f"Found {len(topics)} topics")
    print(topics)

if __name__ == "__main__":
    test()
