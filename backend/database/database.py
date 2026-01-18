import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import uuid


class Database:
    def __init__(self, db_path: str = "quiz_data.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                image_path TEXT,
                extracted_text TEXT,
                topics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Quizzes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                quiz_id TEXT PRIMARY KEY,
                session_id TEXT,
                quiz_data TEXT,
                quiz_type TEXT,
                difficulty TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Submissions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                submission_id TEXT PRIMARY KEY,
                quiz_id TEXT,
                session_id TEXT,
                score REAL,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(quiz_id),
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, image_path: str, extracted_text: str, topics: List[str]) -> str:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_id, image_path, extracted_text, topics)
            VALUES (?, ?, ?, ?)
        """, (session_id, image_path, extracted_text, json.dumps(topics)))
        
        conn.commit()
        conn.close()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return {
            "session_id": row[0],
            "image_path": row[1],
            "extracted_text": row[2],
            "topics": json.loads(row[3]),
            "created_at": row[4]
        }
    
    def save_quiz(self, session_id: str, quiz_data: Dict, quiz_type: str) -> str:
        """Save quiz to database"""
        quiz_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO quizzes (quiz_id, session_id, quiz_data, quiz_type, difficulty)
            VALUES (?, ?, ?, ?, ?)
        """, (
            quiz_id,
            session_id,
            json.dumps(quiz_data),
            quiz_type,
            quiz_data.get("difficulty", "medium")
        ))
        
        conn.commit()
        conn.close()
        return quiz_id
    
    def get_quiz(self, quiz_id: str) -> Optional[Dict]:
        """Get quiz data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT quiz_data FROM quizzes WHERE quiz_id = ?", (quiz_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return json.loads(row[0])
    
    def save_submission(self, quiz_id: str, session_id: str, score: float, results: List[Dict]):
        """Save quiz submission"""
        submission_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO submissions (submission_id, quiz_id, session_id, score, results)
            VALUES (?, ?, ?, ?, ?)
        """, (submission_id, quiz_id, session_id, score, json.dumps(results)))
        
        conn.commit()
        conn.close()
        return submission_id
    
    def get_last_score(self, session_id: str) -> float:
        """Get last quiz score for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT score FROM submissions 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else 50.0  # Default to 50% if no previous score
    
    def get_performance_stats(self, session_id: str) -> Optional[Dict]:
        """Get performance statistics for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all submissions
        cursor.execute("""
            SELECT score, created_at FROM submissions 
            WHERE session_id = ? 
            ORDER BY created_at
        """, (session_id,))
        
        submissions = cursor.fetchall()
        
        if not submissions:
            return None
        
        scores = [s[0] for s in submissions]
        average_score = sum(scores) / len(scores)
        
        # Get session topics
        session = self.get_session(session_id)
        topics = session["topics"] if session else []
        
        # Calculate topic performance (simplified - average score per topic)
        topic_performance = {topic: average_score for topic in topics}
        
        # Quiz history
        quiz_history = [
            {
                "score": score,
                "date": date,
                "quiz_number": i + 1
            }
            for i, (score, date) in enumerate(submissions)
        ]
        
        conn.close()
        
        return {
            "session_id": session_id,
            "total_quizzes": len(submissions),
            "average_score": average_score,
            "topic_performance": topic_performance,
            "quiz_history": quiz_history
        }
