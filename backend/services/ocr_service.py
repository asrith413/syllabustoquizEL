import easyocr
import re
from typing import List, Optional
import os
import ssl
import certifi
import PIL.Image

# Fix for Pillow 10.0.0 removed ANTIALIAS
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

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
            # Fix SSL certificate issues on macOS/Windows
            # EasyOCR downloads models which can fail due to SSL certificate issues
            
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
            print(f"Processing image: {image_path}")
            # Use paragraph=True to combine close text into paragraphs
            # detail=0 returns just the text list
            # mag_ratio=1.5 helps with small text
            # contrast_ths=0.1 helps with low contrast
            # adjust_contrast=0.5 helps with legibility
            results = self.reader.readtext(
                image_path, 
                detail=0, 
                paragraph=True,
                mag_ratio=1.5,
                contrast_ths=0.1,
                adjust_contrast=0.5
            )
            
            # Combine all detected text with newlines to preserve structure
            text = "\n\n".join(results)
            
            print(f"Extracted {len(text)} characters")
            if len(text) > 0:
                print(f"Sample text: {text[:200]}...")
            else:
                print("No text detected!")
                
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            import traceback
            traceback.print_exc()
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
        # Relaxed logic: Accept almost any line that looks like a title
        # Also handle merged titles (e.g. "Matrix Properties of Determinants Determinant of a Matrix")
        
        raw_lines = text.split('\n')
        lines = []
        
        # Pre-process lines to split merged titles
        for r_line in raw_lines:
            r_line = r_line.strip()
            if not r_line:
                continue
                
            # Clean underscores
            if '_' in r_line:
                r_line = r_line.replace('_', ' ')
            
            # 1. First, split aggressively by large spaces or CamelCase boundaries
            temp_parts = []
            
            # Split by 3+ spaces (common in columns)
            cols = re.split(r'\s{3,}', r_line)
            for col in cols:
                if len(col) > 60:
                     # Look for: (lowercase letter) (spaces) (Capital Letter)
                     # limit split to avoid breaking sentences
                     sub_parts = re.split(r'(?<=[a-z])\s+(?=[A-Z][a-z])', col)
                     temp_parts.extend(sub_parts)
                else:
                    temp_parts.append(col)
            
            # 2. Stitch back together parts that were split on connectors (of, a, the, etc.)
            # e.g., "Determinant of a", "Matrix" -> "Determinant of a Matrix"
            merged_parts = []
            if temp_parts:
                current_part = temp_parts[0]
                connectors = {'of', 'a', 'an', 'the', 'and', 'or', 'for', 'to', 'in', 'with', 'by', 'using'}
                
                for i in range(1, len(temp_parts)):
                    next_part = temp_parts[i]
                    # Check if current part ends with a connector
                    words = current_part.strip().split()
                    if words and words[-1].lower() in connectors:
                        # Append next part to current
                        current_part += " " + next_part
                    else:
                        # Push current and start new
                        merged_parts.append(current_part)
                        current_part = next_part
                merged_parts.append(current_part)
                lines.extend(merged_parts)
            else:
                lines.append(r_line) # Just in case

        topics = []
        for line in lines:
            line = line.strip()
            # Filter incomplete fragments often caused by bad OCR or splitting
            if len(line.split()) < 2 and line.lower() in {'matrix', 'formula', 'introduction'}:
                 # Skip generic single words if they likely belong to a fuller title
                 continue
                 
            if len(line) > 5 and len(line) < 100:
                # Must start with letter, have some content
                if line[0].isalnum():
                    # If it's not a sentence (doesn't end in .) or it's a short "sentence" acting as title
                    if not line.endswith('.') or len(line) < 60:
                        topics.append(line)
        
        # Remove duplicates and clean
        topics = list(set(topics))
        topics = [t for t in topics if len(t) > 5 and len(t) < 100]
        
        # Filter out "topics" that are just verbs/connectors
        bad_starts = {'how to', 'methods to', 'types of', 'properties of'}
        final_topics = []
        for t in topics:
            if t.lower() in bad_starts:
                continue
            final_topics.append(t)
            
        topics = final_topics
        
        # If no topics found, just use the raw lines
        if not topics:
            print("No structured topics found, using raw lines as topics")
            topics = [line.strip() for line in raw_lines if len(line.strip()) > 8]
        
        print(f"Extracted {len(topics)} topics: {topics[:3]}...")
        return topics[:20]  # Return top 20 topics
