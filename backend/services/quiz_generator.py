import google.generativeai as genai
import os
import json
import re
from typing import List, Dict, Optional
import traceback
import time
from google.api_core import exceptions

class QuizGenerator:
    def __init__(self):
        print("Initializing Quiz Generator with Gemini API...")
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.models_to_try = []

        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found in environment variables.")
        else:
            try:
                # Force REST transport to avoid gRPC/IPv6 connectivity issues
                genai.configure(api_key=self.api_key, transport='rest')
                
                # 1. List available models
                available_models = []
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            available_models.append(m.name)
                    print(f"Available models: {available_models}")
                except Exception as e:
                    print(f"Could not list models: {e}")
                    # Fallback list if listing fails
                    available_models = ["models/gemini-1.5-flash", "models/gemini-pro"]

                # 2. Build prioritized list of usable models
                # Priority: Flash (fast/cheap) -> Pro (better) -> Legacy
                # We prioritizing models known to produce good JSON output.
                candidates = [
                    "gemini-1.5-flash", 
                    "gemini-flash",
                    "gemini-2.0-flash", 
                    "gemini-1.5-pro",
                    "gemini-pro"
                ]
                
                self.models_to_try = []
                
                # Only add models that match our high-quality candidates list
                for candidate in candidates:
                    for m in available_models:
                        if candidate in m and m not in self.models_to_try:
                            # Filter out obviously incompatible models
                            if "tts" in m or "audio" in m:
                                continue 
                            self.models_to_try.append(m)
                
                # If list is empty (listing failed + no fallback matches), force some defaults
                if not self.models_to_try:
                    self.models_to_try = ["models/gemini-1.5-flash", "models/gemini-pro"]
                    
                print(f"Model priority list: {self.models_to_try}")
                
            except Exception as e:
                print(f"Error configuring Gemini API: {e}")
                self.models_to_try = []

    def generate_quiz(self, topics: List[str], num_questions: int = 10, difficulty: str = "medium", previous_questions: List[str] = None) -> Dict:
        """Generate quiz questions using Gemini API with robust fallback and retries"""
        print(f"Generating {num_questions} questions for topics: {topics[:3]}...")
        
        if not self.models_to_try:
            print("No models available.")
            raise Exception("AI Service Unavailable: No models detected. Please check API Key.")

        prompt = self._create_prompt(topics, num_questions, difficulty, previous_questions)
        
        # Try each model in our priority list
        for model_name in self.models_to_try:
            print(f"Attempting generation with model: {model_name}")
            
            # Aggressive retry logic with significant backoff for Rate Limits
            for attempt in range(3): 
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    return self._parse_gemini_response(response.text, topics, difficulty)
                
                except exceptions.ResourceExhausted:
                    wait_time = 5 * (attempt + 1) # 5s, 10s, 15s
                    print(f"Rate limit hit for {model_name} (Attempt {attempt+1}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    if attempt == 2:
                        print(f"Rate limit persisted for {model_name}. Switching to next model...")
                    
                except Exception as e:
                    print(f"Error with {model_name} (Attempt {attempt+1}): {e}")
                    if attempt == 2: # Last attempt for this model
                        print(f"Model {model_name} failed. Trying next model...")
                    else:
                        time.sleep(2) # Short wait before retry same model
                        
        print("All models failed.")
        # Do NOT fallback to garbage questions. User prefers meaningful error.
        raise Exception("Server Busy: High traffic on AI models. Please try again in 1 minute.")

    def _create_prompt(self, topics: List[str], num_questions: int, difficulty: str, previous_questions: List[str] = None) -> str:
        topics_str = ", ".join(topics)
        
        # Add context about previous questions to avoid repetition
        previous_context = ""
        if previous_questions:
            # Limit to last 20 questions to avoid hitting token limits
            recent_questions = previous_questions[-20:]
            previous_context = f"""
            IMPORTANT: The user has already been asked the following questions. DO NOT repeat them or generate very similar variations. Create FRESH questions.
            Previously asked:
            {json.dumps(recent_questions, indent=2)}
            """

        return f"""
        You are an expert quiz generator. Create {num_questions} multiple-choice questions (MCQs) based on the following topics: {topics_str}.
        
        Difficulty Level: {difficulty}
        {previous_context}
        
        Difficulty Instructions:
        - If "easy": questions should check comprehension and application (Bloom's: Understand/Apply). avoid very simple definitions. Focus on slightly challenging foundational concepts.
        - If "medium": questions should require applying concepts to new situations (Bloom's: Apply/Analyze). Options should be plausible.
        - If "hard": questions should require deep analysis, evaluation, or multi-step problem solving (Bloom's: Evaluate/Create). Options should be subtle.
        
        Format constraints:
        1. Return ONLY a valid JSON array of objects.
        2. Each object must have:
           - "question": string (The question text)
           - "options": array of 4 strings (Possible answers)
           - "correct_answer": integer (0 for A, 1 for B, 2 for C, 3 for D)
           - "bloom_level": string (One of: "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create")
        3. Do not include markdown formatting (like ```json), just the raw JSON string.
        4. Do NOT use LaTeX or markdown formatting for math (no $ symbols).
        5. Use UNICODE text for math symbols where possible to make it look professional (e.g. use "A⁻¹" instead of "A^-1", "x²" instead of "x^2", "θ" instead of "theta", "∫" instead of "integral").
        6. Ensure questions are relevant to the topics provided.
        """

    
    def _parse_gemini_response(self, response_text: str, topics: List[str], difficulty: str) -> Dict:
        """Parse Gemini response with enhanced robustness"""
        try:
            print("Parsing Gemini response...")
            # Clean up potential markdown code blocks
            clean_text = self._clean_response(response_text)
            
            questions = json.loads(clean_text)
            
            # Basic validation
            valid_questions = []
            for q in questions:
                if "question" in q and "options" in q and "correct_answer" in q:
                    if isinstance(q["options"], list) and len(q["options"]) == 4:
                        if "bloom_level" not in q:
                            q["bloom_level"] = "Understand" # Default fallback
                        valid_questions.append(q)
            
            if not valid_questions:
                 raise ValueError("No valid questions parsed")

            return {
                "questions": valid_questions,
                "difficulty": difficulty,
                "topic_count": len(topics)
            }
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Failed to decode JSON from Gemini: {e}")
            print(f"Raw text chunk: {response_text[:200]}...")
            return self._generate_fallback_quiz(topics, len(topics) * 2 or 10, difficulty)
            
    def _clean_response(self, text: str) -> str:
        """Recursive cleaning of JSON string"""
        print(f"DEBUG: Raw response length: {len(text)}")
        
        # 1. Remove Markdown
        if "```json" in text:
            text = text.split("```json")[1]
        if "```" in text:
             text = text.split("```")[0]
             
        text = text.strip()
        
        # 2. Extract first JSON array [ ... ]
        # Sometimes model says "Here is the JSON: [ ... ]"
        start = text.find('[')
        end = text.rfind(']')
        
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]
        
        return text

    def _generate_fallback_quiz(self, topics: List[str], num_questions: int, difficulty: str) -> Dict:
        """Simple rule-based fallback if API fails"""
        questions = []
        topic_count = len(topics)
        
        for i in range(num_questions):
            topic = topics[i % topic_count] if topics else "General Knowledge"
            questions.append({
                "question": f"What is a key aspect of {topic}?",
                "options": [
                    f"It is fundamental to the subject.",
                    "It is unrelated.",
                    "It is deprecated.",
                    "None of the above."
                ],
                "correct_answer": 0
            })
            
        return {
            "questions": questions,
            "difficulty": difficulty,
            "topic_count": len(topics)
        }
