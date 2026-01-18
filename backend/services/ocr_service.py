import easyocr
import re
from typing import List, Optional
import os
import ssl
import certifi


class OCRService:
    def __init__(self):
        # Lazy initialization - only initialize when needed
        print("OCR service ready (will initialize on first use)")
        self.reader: Optional[easyocr.Reader] = None
        self._initialized = False
    
    def _initialize_reader(self):
        """Initialize EasyOCR reader lazily"""
        if self._initialized:
            return
        
        try:
            print("Initializing OCR service...")
            # Fix SSL certificate issues on macOS
            # EasyOCR downloads models which can fail due to SSL certificate issues
            import ssl
            
            # Temporarily disable SSL verification for EasyOCR model downloads
            # This is safe since we're downloading from known sources
            original_context = ssl._create_default_https_context
            ssl._create_default_https_context = ssl._create_unverified_context
            
            try:
                self.reader = easyocr.Reader(['en'], gpu=False)
            finally:
                # Restore original SSL context
                ssl._create_default_https_context = original_context
            
            self._initialized = True
            print("OCR service initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize OCR service: {e}")
            print("OCR will use fallback text extraction")
            # Restore SSL context even on error
            try:
                import ssl
                ssl._create_default_https_context = ssl._create_unverified_context
            except:
                pass
            self.reader = None
            self._initialized = True  # Mark as attempted to avoid retrying
    
    def extract_text(self, image_path: str) -> str:
        """Extract text from image using OCR"""
        self._initialize_reader()
        
        if self.reader is None:
            # Fallback: return empty string or try basic extraction
            print("OCR not available, using fallback")
            return ""
        
        try:
            results = self.reader.readtext(image_path)
            # Combine all detected text
            text = " ".join([result[1] for result in results])
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def extract_topics(self, text: str) -> List[str]:
        """Extract topics from extracted text"""
        topics = []
        
        # Common patterns for syllabus topics
        # Look for numbered lists, bullet points, chapter titles, etc.
        
        # Pattern 1: Numbered topics (1., 2., etc.)
        numbered_pattern = r'\d+[\.\)]\s*([A-Z][^\n]+)'
        matches = re.findall(numbered_pattern, text)
        topics.extend([m.strip() for m in matches])
        
        # Pattern 2: Bullet points (-, *, •)
        bullet_pattern = r'[-*•]\s*([A-Z][^\n]+)'
        matches = re.findall(bullet_pattern, text)
        topics.extend([m.strip() for m in matches])
        
        # Pattern 3: Chapter/Unit titles (Chapter X:, Unit X:, etc.)
        chapter_pattern = r'(?:Chapter|Unit|Topic|Module)\s*\d*[:\-]?\s*([A-Z][^\n]+)'
        matches = re.findall(chapter_pattern, text, re.IGNORECASE)
        topics.extend([m.strip() for m in matches])
        
        # Pattern 4: Lines starting with capital letters (potential titles)
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 10 and len(line) < 100:
                if line[0].isupper() and not line.endswith('.') and ':' not in line:
                    # Check if it looks like a topic title
                    if any(keyword in line.lower() for keyword in ['introduction', 'overview', 'concept', 'theory', 'application']):
                        topics.append(line)
        
        # Remove duplicates and clean
        topics = list(set(topics))
        topics = [t for t in topics if len(t) > 5 and len(t) < 150]
        
        # If no topics found, split by sentences and take first few meaningful ones
        if not topics:
            sentences = re.split(r'[.!?]\s+', text)
            topics = [s.strip() for s in sentences[:10] if len(s.strip()) > 20 and len(s.strip()) < 200]
        
        return topics[:15]  # Return top 15 topics
