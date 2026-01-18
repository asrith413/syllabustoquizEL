from typing import Dict, List


class AdaptiveQuizService:
    """Service for managing adaptive quiz difficulty"""
    
    def determine_difficulty(self, score: float) -> str:
        """Determine next quiz difficulty based on score"""
        if score < 60:
            return "easy"
        elif score >= 80:
            return "hard"
        else:
            return "medium"
    
    def adjust_question_complexity(self, questions: List[Dict], difficulty: str) -> List[Dict]:
        """Adjust question complexity based on difficulty"""
        adjusted = []
        
        for q in questions:
            if difficulty == "easy":
                # Simplify questions
                q["question"] = q["question"].replace("advanced", "basic")
                q["question"] = q["question"].replace("complex", "simple")
            elif difficulty == "hard":
                # Make questions more challenging
                q["question"] = q["question"].replace("basic", "advanced")
                q["question"] = q["question"].replace("simple", "complex")
            
            adjusted.append(q)
        
        return adjusted
