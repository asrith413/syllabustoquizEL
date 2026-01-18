from pydantic import BaseModel
from typing import List, Dict, Optional


class UploadResponse(BaseModel):
    session_id: str
    message: str
    topics: List[str]


class TopicListResponse(BaseModel):
    topics: List[str]


class QuizRequest(BaseModel):
    session_id: str
    num_questions: Optional[int] = 18


class Question(BaseModel):
    question: str
    options: List[str]
    correct_answer: int


class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[Dict]
    session_id: str


class QuizSubmission(BaseModel):
    quiz_id: str
    session_id: str
    answers: Dict[str, int]


class ResultItem(BaseModel):
    question_index: int
    user_answer: Optional[int]
    correct_answer: int
    is_correct: bool


class SubmissionResponse(BaseModel):
    score: float
    correct: int
    total: int
    results: List[ResultItem]
    next_difficulty: str


class PerformanceStats(BaseModel):
    session_id: str
    total_quizzes: int
    average_score: float
    topic_performance: Dict[str, float]
    quiz_history: List[Dict]
