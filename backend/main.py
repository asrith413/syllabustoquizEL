from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime

from services.ocr_service import OCRService
from services.quiz_generator import QuizGenerator
from services.adaptive_quiz import AdaptiveQuizService
from database.database import Database
from models.schemas import (
    UploadResponse, TopicListResponse, QuizRequest, 
    QuizResponse, QuizSubmission, SubmissionResponse,
    PerformanceStats
)

app = FastAPI(title="Syllabus to Quiz API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (OCR is lazy-loaded to avoid SSL issues at startup)
ocr_service = OCRService()
quiz_generator = QuizGenerator()
adaptive_service = AdaptiveQuizService()
db = Database()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """Upload syllabus image and extract topics"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text using OCR
        extracted_text = ocr_service.extract_text(str(file_path))
        
        # Extract topics
        topics = ocr_service.extract_topics(extracted_text)
        
        # Store in database
        session_id = db.create_session(str(file_path), extracted_text, topics)
        
        return UploadResponse(
            session_id=session_id,
            message="Image uploaded successfully",
            topics=topics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/topics/{session_id}", response_model=TopicListResponse)
async def get_topics(session_id: str):
    """Get topics for a session"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return TopicListResponse(topics=session["topics"])


@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate initial quiz based on topics"""
    try:
        session = db.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Generate quiz
        quiz = quiz_generator.generate_quiz(
            topics=session["topics"],
            num_questions=request.num_questions or 18,
            difficulty="medium"
        )
        
        # Store quiz in database
        quiz_id = db.save_quiz(request.session_id, quiz, "initial")
        
        return QuizResponse(
            quiz_id=quiz_id,
            questions=quiz["questions"],
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit-quiz", response_model=SubmissionResponse)
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    try:
        quiz = db.get_quiz(submission.quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Calculate score
        correct = 0
        total = len(quiz["questions"])
        results = []
        
        for i, question in enumerate(quiz["questions"]):
            user_answer = submission.answers.get(str(i))
            correct_answer = question["correct_answer"]
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct += 1
            
            results.append({
                "question_index": i,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })
        
        score_percentage = (correct / total) * 100
        
        # Save submission
        db.save_submission(
            submission.quiz_id,
            submission.session_id,
            score_percentage,
            results
        )
        
        # Determine difficulty for next quiz
        difficulty = "easy" if score_percentage < 60 else "hard" if score_percentage >= 80 else "medium"
        
        return SubmissionResponse(
            score=score_percentage,
            correct=correct,
            total=total,
            results=results,
            next_difficulty=difficulty
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-adaptive-quiz", response_model=QuizResponse)
async def generate_adaptive_quiz(request: QuizRequest):
    """Generate adaptive quiz based on previous performance"""
    try:
        session = db.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get previous quiz performance
        previous_score = db.get_last_score(request.session_id)
        
        # Determine difficulty
        if previous_score < 60:
            difficulty = "easy"
        elif previous_score >= 80:
            difficulty = "hard"
        else:
            difficulty = "medium"
        
        # Generate adaptive quiz
        quiz = quiz_generator.generate_quiz(
            topics=session["topics"],
            num_questions=request.num_questions or 18,
            difficulty=difficulty
        )
        
        # Store quiz
        quiz_id = db.save_quiz(request.session_id, quiz, f"adaptive_{difficulty}")
        
        return QuizResponse(
            quiz_id=quiz_id,
            questions=quiz["questions"],
            session_id=request.session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/{session_id}", response_model=PerformanceStats)
async def get_stats(session_id: str):
    """Get performance statistics for a session"""
    stats = db.get_performance_stats(session_id)
    if not stats:
        raise HTTPException(status_code=404, detail="No stats found")
    
    return PerformanceStats(**stats)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
