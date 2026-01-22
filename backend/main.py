from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix for IPv6/gRPC connectivity issues
os.environ["GRPC_DNS_RESOLVER"] = "native"

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
import shutil
from typing import List, Dict, Optional
import json
from datetime import datetime

from services.ocr_service import OCRService
from services.quiz_generator import QuizGenerator
from services.adaptive_quiz import AdaptiveQuizService
from services.auth import verify_password, get_password_hash, create_access_token, get_current_user_id
from database.database import Database
from models.schemas import (
    UploadResponse, TopicListResponse, QuizRequest, 
    QuizResponse, QuizSubmission, SubmissionResponse,
    PerformanceStats, UserCreate, UserLogin, Token
)

app = FastAPI(title="SocratAI API")

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
db = Database(db_path=str(Path(__file__).parent / "quiz_data.db"))

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    # Check if user exists
    existing_user = db.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    try:
        user_id = db.create_user(user.email, user.username, hashed_password)
        
        # Create access token
        access_token = create_access_token(data={"sub": user_id})
        return {"access_token": access_token, "token_type": "bearer", "username": user.username}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin): # Using JSON body instead of OAuth2Form for simplicity with React
    user = db.get_user_by_email(user_credentials.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not verify_password(user_credentials.password, user["hashed_password"]):
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(data={"sub": user["user_id"]})
    return {"access_token": access_token, "token_type": "bearer", "username": user["username"]}


@app.get("/api/history")
async def get_history(user_id: str = Depends(get_current_user_id)):
    """Get user's history"""
    return db.get_user_history(user_id)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    """Upload syllabus image and extract topics"""
    try:
        # Save uploaded file
        file_path = UPLOAD_DIR / f"{user_id}_{file.filename}" # Prefix with user_id to avoid collisions
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text using OCR
        extracted_text = ocr_service.extract_text(str(file_path))
        
        # Extract topics
        topics = ocr_service.extract_topics(extracted_text)
        
        # Store in database
        session_id = db.create_session(user_id, str(file_path), extracted_text, topics)
        
        return UploadResponse(
            session_id=session_id,
            message="Image uploaded successfully",
            topics=topics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/topics/{session_id}", response_model=TopicListResponse)
async def get_topics(session_id: str, user_id: str = Depends(get_current_user_id)):
    """Get topics for a session"""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Ownership check
    if session.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this session")
    
    return TopicListResponse(topics=session["topics"])


@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, user_id: str = Depends(get_current_user_id)):
    """Generate initial quiz based on topics"""
    try:
        session = db.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        if session.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Generate quiz
        quiz = quiz_generator.generate_quiz(
            topics=session["topics"],
            num_questions=request.num_questions or 18,
            difficulty="easy"
        )
        
        # Store quiz in database
        quiz_id = db.save_quiz(request.session_id, quiz, "initial")
        
        return QuizResponse(
            quiz_id=quiz_id,
            questions=quiz["questions"],
            session_id=request.session_id
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ERROR in generate_quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/submit-quiz", response_model=SubmissionResponse)
async def submit_quiz(submission: QuizSubmission, user_id: str = Depends(get_current_user_id)):
    """Submit quiz answers and get results"""
    try:
        # Verify session ownership via quiz or session
        # Ideally we check if quiz belongs to a session owned by user.
        # Currently db.get_quiz doesn't return session_id directly in the easiest way without joining.
        # But we pass session_id in submission.
        
        session = db.get_session(submission.session_id)
        if not session or session.get("user_id") != user_id:
             raise HTTPException(status_code=403, detail="Not authorized")

        quiz = db.get_quiz(submission.quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        # Calculate stats
        correct = 0
        total = len(quiz["questions"])
        results = []
        total_time_correct = 0
        correct_count_for_time = 0
        
        for i, question in enumerate(quiz["questions"]):
            q_idx_str = str(i)
            user_answer = submission.answers.get(q_idx_str)
            correct_answer = question["correct_answer"]
            is_correct = user_answer == correct_answer
            
            # Extract time for this question
            time_spent = 0
            if submission.time_taken:
                # Keys in time_taken might be integers (from frontend) or strings (restored from JSON)
                # Pydantic model defines it as Dict[int, float], so keys should be ints.
                time_spent = submission.time_taken.get(i, 0)
            
            if is_correct:
                correct += 1
                total_time_correct += time_spent
                correct_count_for_time += 1
            
            results.append({
                "question_index": i,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
                "time_taken": time_spent # Store in DB
            })
        
        score_percentage = (correct / total) * 100
        avg_time_correct = (total_time_correct / correct_count_for_time) if correct_count_for_time > 0 else 0
        
        # Save submission
        db.save_submission(
            submission.quiz_id,
            submission.session_id,
            score_percentage,
            results
        )
        
        # Determine difficulty for next quiz
        # Logic: 
        # > 80%: Promote (Always)
        # 60-80%: 
        #    Fast (<30s): Promote
        #    Slow (>30s): Maintain
        # < 60%: Demote
        
        current_difficulty = quiz.get("difficulty", "medium")
        difficulty = current_difficulty # Default stay same
        
        if score_percentage >= 80:
             # Promote
             difficulty = "medium" if current_difficulty == "easy" else "hard"
             
        elif score_percentage >= 60:
             # Check Speed
             if avg_time_correct > 0 and avg_time_correct < 30:
                 # Fast! Promote
                 difficulty = "medium" if current_difficulty == "easy" else "hard"
             else:
                 # Slow or just right. Maintain.
                 difficulty = current_difficulty
                 
        else: # < 60%
             # Demote
             difficulty = "easy" if current_difficulty == "medium" else "medium" if current_difficulty == "hard" else "easy"
        
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
async def generate_adaptive_quiz(request: QuizRequest, user_id: str = Depends(get_current_user_id)):
    """Generate adaptive quiz based on previous performance"""
    try:
        session = db.get_session(request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        if session.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
            
        # Get previous quiz performance
        previous_score = db.get_last_score(request.session_id)
        
        # Get previous quiz to determine its difficulty
        # Ideally we store difficulty in submissions or get the last quiz directly
        # For now, we'll infer it or default to medium if we can't look it up easily. 
        # But wait, we need to know the CURRENT level to increment.
        # Let's try to get the last quiz for this session to see its difficulty.
        
        last_quiz_difficulty = "medium" # Default
        
        # We need a proper way to get the last quiz's difficulty.
        # This requires a new DB method or query. 
        # For this prototype, let's use a simplified heuristic based on score only if we can't track state,
        # BUT the user specifically requested smooth transitions.
        # So let's implement get_last_quiz_difficulty in DB or just peek at recent history.
        
        last_difficulty = db.get_last_quiz_difficulty(request.session_id) or "easy" # Default to easy if first adaptive
        
        if previous_score < 60:
             difficulty = "easy" if last_difficulty == "medium" else "medium" if last_difficulty == "hard" else "easy"
        elif previous_score >= 80:
             difficulty = "medium" if last_difficulty == "easy" else "hard"
        else:
             difficulty = last_difficulty
        
        # Get all previous questions for this session to avoid repetition
        previous_questions = db.get_all_questions_for_session(request.session_id)
        
        # Generate adaptive quiz
        quiz = quiz_generator.generate_quiz(
            topics=session["topics"],
            num_questions=request.num_questions or 18,
            difficulty=difficulty,
            previous_questions=previous_questions
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
async def get_stats(session_id: str, user_id: str = Depends(get_current_user_id)):
    """Get performance statistics for a session"""
    session = db.get_session(session_id)
    # Check ownership
    if session and session.get("user_id") != user_id:
         raise HTTPException(status_code=403, detail="Not authorized")

    stats = db.get_performance_stats(session_id)
    if not stats:
        raise HTTPException(status_code=404, detail="No stats found")
    
    return PerformanceStats(**stats)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
