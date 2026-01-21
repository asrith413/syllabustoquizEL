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
                genai.configure(api_key=self.api_key)
                
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
                # We prioritize newer flash models as they are usually most generous with free tier
                candidates = [
                    "gemini-1.5-flash", 
                    "gemini-flash",
                    "gemini-2.0-flash", 
                    "gemini-1.5-pro",
                    "gemini-pro"
                ]
                
                self.models_to_try = []
                
                # Add matched candidates first
                for candidate in candidates:
                    for m in available_models:
                        if candidate in m and m not in self.models_to_try:
                            self.models_to_try.append(m)
                
                # Add any remaining available models that weren't in our candidate list
                # This ensures we don't miss any obscure working model associated with the key
                for m in available_models:
                    if m not in self.models_to_try:
                        self.models_to_try.append(m)
                
                # If list is empty (listing failed + no fallback matches), force some defaults
                if not self.models_to_try:
                    self.models_to_try = ["models/gemini-1.5-flash", "models/gemini-pro"]
                    
                print(f"Model priority list: {self.models_to_try}")
                
            except Exception as e:
                print(f"Error configuring Gemini API: {e}")
                self.models_to_try = []

    def generate_quiz(self, topics: List[str], num_questions: int = 10, difficulty: str = "medium") -> Dict:
        """Generate quiz questions using Gemini API with robust fallback and retries"""
        print(f"Generating {num_questions} questions for topics: {topics[:3]}...")
        
        if not self.models_to_try:
            print("No models available, using basic fallback.")
            return self._generate_fallback_quiz(topics, num_questions, difficulty)

        prompt = self._create_prompt(topics, num_questions, difficulty)
        
        # Try each model in our priority list
        for model_name in self.models_to_try:
            print(f"Attempting generation with model: {model_name}")
            
            # Simple retry logic for transient errors on the SAME model
            for attempt in range(2): 
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    return self._parse_gemini_response(response.text, topics, difficulty)
                
                except exceptions.ResourceExhausted:
                    print(f"Rate limit hit for {model_name}. Switching to next model...")
                    # Break inner loop to try next model immediately
                    break 
                    
                except Exception as e:
                    print(f"Error with {model_name} (Attempt {attempt+1}): {e}")
                    if attempt == 1: # Last attempt for this model
                        print(f"Model {model_name} failed. Trying next model...")
                    else:
                        time.sleep(1) # Short wait before retry same model
                        
        print("All models failed. Using rule-based fallback.")
        return self._generate_fallback_quiz(topics, num_questions, difficulty)

    def _create_prompt(self, topics: List[str], num_questions: int, difficulty: str) -> str:
        topics_str = ", ".join(topics)
        return f"""
        You are an expert quiz generator. Create {num_questions} multiple-choice questions (MCQs) based on the following topics: {topics_str}.
        
        Difficulty Level: {difficulty}
        
        Format constraints:
        1. Return ONLY a valid JSON array of objects.
        2. Each object must have:
           - "question": string (The question text)
           - "options": array of 4 strings (Possible answers)
           - "correct_answer": integer (0 for A, 1 for B, 2 for C, 3 for D)
        3. Do not include markdown formatting (like ```json), just the raw JSON string.
        4. Do NOT use LaTeX or markdown formatting for math (no $ symbols).
        5. Use UNICODE text for math symbols where possible to make it look professional (e.g. use "A⁻¹" instead of "A^-1", "x²" instead of "x^2", "θ" instead of "theta", "∫" instead of "integral").
        6. Ensure questions are relevant to the topics provided.
        """

    def _parse_gemini_response(self, response_text: str, topics: List[str], difficulty: str) -> Dict:
        try:
            # Clean up potential markdown code blocks
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            
            questions = json.loads(clean_text)
            
            # Basic validation
            valid_questions = []
            for q in questions:
                if "question" in q and "options" in q and "correct_answer" in q:
                    if isinstance(q["options"], list) and len(q["options"]) == 4:
                        valid_questions.append(q)
            
            return {
                "questions": valid_questions,
                "difficulty": difficulty,
                "topic_count": len(topics)
            }
        except json.JSONDecodeError:
            print(f"Failed to decode JSON from Gemini: {response_text[:100]}...")
            return self._generate_fallback_quiz(topics, 1, difficulty)

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
