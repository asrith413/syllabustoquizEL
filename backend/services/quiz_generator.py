from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Dict
import json
import re


class QuizGenerator:
    def __init__(self):
        print("Initializing Quiz Generator...")
        # Use Phi-3-mini for quiz generation (smaller, faster, free)
        # If model download fails, will use rule-based generation
        model_name = "microsoft/Phi-3-mini-4k-instruct"
        
        self.model = None
        self.tokenizer = None
        
        try:
            print("Attempting to load Phi-3 model (this may take a few minutes on first run)...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
                low_cpu_mem_usage=True
            )
            print("Quiz Generator initialized successfully with Phi-3")
        except Exception as e:
            print(f"Error loading Phi-3: {e}")
            print("Note: Model download requires internet connection and ~7GB disk space")
            print("Falling back to rule-based generation (works offline)")
            self.model = None
            self.tokenizer = None
    
    def generate_quiz(self, topics: List[str], num_questions: int = 18, difficulty: str = "medium") -> Dict:
        """Generate quiz questions based on topics"""
        
        if self.model is None:
            return self._generate_rule_based_quiz(topics, num_questions, difficulty)
        
        try:
            return self._generate_llm_quiz(topics, num_questions, difficulty)
        except Exception as e:
            print(f"LLM generation failed: {e}, falling back to rule-based")
            return self._generate_rule_based_quiz(topics, num_questions, difficulty)
    
    def _generate_llm_quiz(self, topics: List[str], num_questions: int, difficulty: str) -> Dict:
        """Generate quiz using Phi-3 model"""
        topics_text = ", ".join(topics[:10])  # Use first 10 topics
        
        prompt = f"""Generate {num_questions} multiple choice questions (MCQs) based on these topics: {topics_text}

Difficulty level: {difficulty}

Format each question as JSON:
{{
  "question": "Question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0
}}

Return only valid JSON array of questions. Make questions {difficulty} level - {"simple and straightforward" if difficulty == "easy" else "challenging and detailed" if difficulty == "hard" else "moderate complexity"}.
"""
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that generates educational quiz questions."},
            {"role": "user", "content": prompt}
        ]
        
        inputs = self.tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt"
        )
        
        if torch.cuda.is_available():
            inputs = inputs.to("cuda")
        
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_new_tokens=2048,
                temperature=0.7,
                do_sample=True,
                top_p=0.9
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            questions = json.loads(json_match.group())
        else:
            # Fallback: try to parse questions manually
            questions = self._parse_questions_from_text(response)
        
        # Ensure we have the right number of questions
        if len(questions) < num_questions:
            # Generate more using rule-based
            additional = self._generate_rule_based_questions(topics, num_questions - len(questions), difficulty)
            questions.extend(additional)
        
        return {
            "questions": questions[:num_questions],
            "difficulty": difficulty,
            "topic_count": len(topics)
        }
    
    def _parse_questions_from_text(self, text: str) -> List[Dict]:
        """Parse questions from LLM text response"""
        questions = []
        # Simple parsing logic
        question_blocks = re.split(r'\n\s*\n', text)
        
        for block in question_blocks:
            if '?' in block:
                lines = block.split('\n')
                question = ""
                options = []
                correct = 0
                
                for line in lines:
                    if '?' in line:
                        question = line.strip()
                    elif re.match(r'^[A-D][\.\)]', line):
                        options.append(re.sub(r'^[A-D][\.\)]\s*', '', line).strip())
                    elif 'correct' in line.lower():
                        match = re.search(r'([A-D])', line)
                        if match:
                            correct = ord(match.group(1)) - ord('A')
                
                if question and len(options) == 4:
                    questions.append({
                        "question": question,
                        "options": options,
                        "correct_answer": correct
                    })
        
        return questions
    
    def _generate_rule_based_quiz(self, topics: List[str], num_questions: int, difficulty: str) -> Dict:
        """Generate quiz using rule-based approach"""
        questions = []
        
        # Use all topics, cycling if needed
        topic_index = 0
        question_templates = [
            ("What is the main concept of {topic}?", [
                "The fundamental principles and core ideas",
                "Advanced theoretical frameworks",
                "Practical applications only",
                "None of the above"
            ]),
            ("Which aspect is most important in {topic}?", [
                "Understanding core concepts",
                "Memorizing facts",
                "Avoiding the topic",
                "None of the above"
            ]),
            ("How does {topic} relate to the overall subject?", [
                "It's an integral part of the subject",
                "It's completely separate",
                "It's optional content",
                "None of the above"
            ]),
            ("What would be a key characteristic of {topic}?", [
                "Relevant and important concepts",
                "Unrelated information",
                "Outdated material",
                "None of the above"
            ]),
        ]
        
        for i in range(num_questions):
            topic = topics[topic_index % len(topics)]
            template_idx = i % len(question_templates)
            question_template, default_options = question_templates[template_idx]
            
            # Adjust based on difficulty
            if difficulty == "easy":
                question = question_template.format(topic=topic)
                options = [
                    default_options[0],  # Usually correct
                    f"Something unrelated to {topic}",
                    f"An advanced concept in {topic}",
                    "None of the above"
                ]
            elif difficulty == "hard":
                question = f"Which of the following best describes advanced understanding of {topic}?"
                options = [
                    f"Deep knowledge of {topic} principles and applications",
                    f"Basic introduction to {topic}",
                    f"Simple overview of {topic}",
                    f"Superficial knowledge of {topic}"
                ]
            else:  # medium
                question = question_template.format(topic=topic)
                options = [
                    default_options[0],
                    default_options[1] if len(default_options) > 1 else f"Alternative view of {topic}",
                    default_options[2] if len(default_options) > 2 else f"Different aspect of {topic}",
                    "None of the above"
                ]
            
            questions.append({
                "question": question,
                "options": options,
                "correct_answer": 0
            })
            
            topic_index += 1
        
        return {
            "questions": questions[:num_questions],
            "difficulty": difficulty,
            "topic_count": len(topics)
        }
    
    def _generate_rule_based_questions(self, topics: List[str], count: int, difficulty: str) -> List[Dict]:
        """Generate additional rule-based questions"""
        questions = []
        question_templates = [
            "What is the primary focus of {topic}?",
            "Which aspect is most important in {topic}?",
            "How does {topic} relate to the overall subject?",
            "What would be a key characteristic of {topic}?",
        ]
        
        for i in range(count):
            topic = topics[i % len(topics)]
            template = question_templates[i % len(question_templates)]
            
            question = template.format(topic=topic)
            options = [
                f"Option A related to {topic}",
                f"Option B related to {topic}",
                f"Option C related to {topic}",
                f"Option D related to {topic}"
            ]
            
            questions.append({
                "question": question,
                "options": options,
                "correct_answer": 0
            })
        
        return questions
