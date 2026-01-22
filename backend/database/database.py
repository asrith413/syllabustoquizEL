import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import os
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
        
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                username TEXT,
                hashed_password TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table (updated with user_id)
        # Note: SQLite doesn't support easy column addition if it doesn't exist in a simple IF check without querying schema.
        # For this prototype, we'll try to add it blindly or handle the error, or just recreate if simpler.
        # Since we want to preserve data, we'll try to add the column.
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                image_path TEXT,
                extracted_text TEXT,
                topics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Attempt to add user_id column to existing sessions table if it was created before
        try:
            cursor.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT REFERENCES users(user_id)")
        except sqlite3.OperationalError:
            # Column likely already exists
            pass

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

    def create_user(self, email: str, username: str, hashed_password: str) -> str:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO users (user_id, email, username, hashed_password)
                VALUES (?, ?, ?, ?)
            """, (user_id, email, username, hashed_password))
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            raise ValueError("Email already exists")
        finally:
            conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
            
        return {
            "user_id": row[0],
            "email": row[1],
            "username": row[2],
            "hashed_password": row[3],
            "created_at": row[4]
        }
    
    def create_session(self, user_id: str, image_path: str, extracted_text: str, topics: List[str]) -> str:
        """Create a new session (linked to user)"""
        session_id = str(uuid.uuid4())
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, image_path, extracted_text, topics)
            VALUES (?, ?, ?, ?, ?)
        """, (session_id, user_id, image_path, extracted_text, json.dumps(topics)))
        
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
            
        # Dynamically map indices to column names to handle schema variations (Fresh vs Migrated)
        col_names = [description[0] for description in cursor.description]
        row_dict = dict(zip(col_names, row))
        
        # Helper to safely parse JSON topics
        def parse_topics(data):
            if not data:
                return []
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                # Fallback schemes
                try:
                    if isinstance(data, str) and (data.startswith('"') or data.startswith("'")):
                            return json.loads(json.loads(data))
                except: pass
                if str(data).startswith("[") and str(data).endswith("]"):
                        inner = str(data)[1:-1]
                        return [t.strip().strip("'").strip('"') for t in inner.split(",")]
                return [str(data)]

        return {
            "session_id": row_dict.get("session_id"),
            "user_id": row_dict.get("user_id"), # Will be None if column doesn't exist (old schema)
            "image_path": row_dict.get("image_path"),
            "extracted_text": row_dict.get("extracted_text"),
            "topics": parse_topics(row_dict.get("topics")),
            "created_at": row_dict.get("created_at")
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
    
    def get_last_quiz_difficulty(self, session_id: str) -> Optional[str]:
        """Get the difficulty of the last generated quiz for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT difficulty FROM quizzes 
            WHERE session_id = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        """, (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
        
    def get_all_questions_for_session(self, session_id: str) -> List[str]:
        """Get all question texts previously generated for this session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT quiz_data FROM quizzes WHERE session_id = ?", (session_id,))
        rows = cursor.fetchall()
        
        questions = []
        for row in rows:
            try:
                quiz_data = json.loads(row[0])
                for q in quiz_data.get("questions", []):
                    questions.append(q["question"])
            except:
                pass
                
        conn.close()
        return questions
    
    def get_performance_stats(self, session_id: str) -> Optional[Dict]:
        """Get performance statistics for a session"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all submissions linked to this session
        cursor.execute("""
            SELECT s.score, s.created_at, s.results, q.quiz_data 
            FROM submissions s
            JOIN quizzes q ON s.quiz_id = q.quiz_id
            WHERE s.session_id = ? 
            ORDER BY s.created_at
        """, (session_id,))
        
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return None
        
        scores = [row[0] for row in rows]
        average_score = sum(scores) / len(scores)
        
        # Calculate Bloom's Performance (Accuracy & Time)
        bloom_counts = {}   # {level: total_questions}
        bloom_correct = {}  # {level: correct_answers}
        bloom_time_sum = {} # {level: total_seconds_spent}
        bloom_time_count = {} # {level: count_of_timed_questions}
        
        # Initialize standard levels to ensure they appear
        standard_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        for level in standard_levels:
            bloom_counts[level] = 0
            bloom_correct[level] = 0
            bloom_time_sum[level] = 0
            bloom_time_count[level] = 0
            
        for row in rows:
            try:
                # row[2] is submission results (JSON), row[3] is quiz_data (JSON)
                results = json.loads(row[2])
                quiz = json.loads(row[3])
                questions = quiz["questions"]
                
                # Create a map of question index to bloom level
                q_bloom_map = {}
                for i, q in enumerate(questions):
                     q_bloom_map[i] = q.get("bloom_level", "Understand")
                
                for res in results:
                    idx = res.get("question_index")
                    is_correct = res.get("is_correct")
                    time_taken = res.get("time_taken", 0) # Use 0 if missing (old data)
                    
                    if idx is not None and idx in q_bloom_map:
                        level = q_bloom_map[idx]
                        bloom_counts[level] = bloom_counts.get(level, 0) + 1
                        if is_correct:
                            bloom_correct[level] = bloom_correct.get(level, 0) + 1
                            
                        # Track time (all questions, or just correct? Usually all is useful for "effort")
                        if time_taken > 0:
                            bloom_time_sum[level] = bloom_time_sum.get(level, 0) + time_taken
                            bloom_time_count[level] = bloom_time_count.get(level, 0) + 1
                            
            except Exception as e:
                print(f"Error calculating stats for row: {e}")
                continue
                
        # Calculate percentages & averages
        bloom_performance = {}
        bloom_time_performance = {}
        
        for level in bloom_counts:
            # Accuracy
            if bloom_counts[level] > 0:
                bloom_performance[level] = (bloom_correct[level] / bloom_counts[level]) * 100
            else:
                bloom_performance[level] = 0.0
            
            # Average Time
            if bloom_time_count[level] > 0:
                bloom_time_performance[level] = bloom_time_sum[level] / bloom_time_count[level]
            else:
                bloom_time_performance[level] = 0.0

        # Get session topics
        session = self.get_session(session_id)
        if session and "topics" in session:
            topics = session["topics"]
        else:
            topics = []
        
        # Calculate topic performance (simplified - average score per topic)
        topic_performance = {topic: average_score for topic in topics}
        
        # Quiz history
        quiz_history = [
            {
                "score": row[0],
                "date": row[1],
                "quiz_number": i + 1
            }
            for i, row in enumerate(rows)
        ]
        
        conn.close()
        
        return {
            "session_id": session_id,
            "total_quizzes": len(rows),
            "average_score": average_score,
            "topic_performance": topic_performance,
            "bloom_performance": bloom_performance,
            "bloom_time_performance": bloom_time_performance,
            "quiz_history": quiz_history
        }

    def get_user_history(self, user_id: str) -> List[Dict]:
        """Get all sessions/quizzes for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get sessions with their image paths and last quiz score
        cursor.execute("""
            SELECT s.session_id, s.topics, s.image_path, s.created_at,
                   (SELECT score FROM submissions sub 
                    WHERE sub.session_id = s.session_id 
                    ORDER BY sub.created_at DESC LIMIT 1) as last_score
            FROM sessions s
            WHERE s.user_id = ?
            ORDER BY s.created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            # Map absolute path back to relative path for serving
            # Assuming 'uploads' is always in the path
            image_path = row[2]
            relative_image_path = None
            if image_path:
                try:
                    # Very simple logic: if "uploads" in path, take that part
                    if "uploads" in image_path:
                        relative_image_path = "uploads/" + image_path.split("uploads")[-1].lstrip(os.sep).lstrip("/")
                    else:
                        relative_image_path = image_path # Fallback
                except:
                    pass

            history.append({
                "session_id": row[0],
                "topics": json.loads(row[1]) if row[1] else [],
                "image_path": relative_image_path,
                "last_score": row[4], # Can be None
                "created_at": row[3]
            })
        return history
