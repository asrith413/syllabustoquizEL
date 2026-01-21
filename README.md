# SocratAI 🎓

**SocratAI** is an intelligent, adaptive quiz platform that transforms syllabus images into personalized learning experiences. Powered by **Google Gemini AI** and **EasyOCR**, it analyses your learning material to generate high-quality questions, adapts to your performance level, and tracks your cognitive growth using **Bloom's Taxonomy**.

## ✨ Key Features

*   **📸 Syllabus to Quiz**: Upload an image of any syllabus or textbook page. The system automatically extracts text and identifies key topics.
*   **🧠 Intelligent Question Generation**: Powered by **Google Gemini**, creating valid MCQs with distinct difficulty levels (Easy, Medium, Hard).
*   **🔄 Adaptive Learning**: The difficulty evolves based on your performance.
    *   **Smooth Progression**: Difficulty increases gradually (Easy → Medium → Hard) to ensure steady learning.
    *   **Anti-Repetition**: The AI remembers previous questions in a session and avoids repeating them.
*   **📊 Bloom's Taxonomy Analytics**:
    *   Questions are tagged by cognitive level (Remember, Apply, Analyze, etc.).
    *   **Radar Charts** visualize your strengths and weaknesses across these cognitive domains.
*   **🔐 Secure Authentication**: Full user system with Sign Up/Login, JWT authentication, and secure password hashing.
*   **🎨 Enhaced UX**: A clean, modern interface with expandable results, detailed feedback, and no auto-redirects.

## 🛠️ Technology Stack

### Backend
*   **Framework**: FastAPI (Python)
*   **Database**: SQLite (local)
*   **AI Engine**: Google Gemini API (Content Generation)
*   **OCR Engine**: EasyOCR (Local Text Extraction)
*   **Auth**: Python-Jose (JWT) + Passlib (Bcrypt)

### Frontend
*   **Framework**: Next.js 14 (React)
*   **Styling**: Tailwind CSS
*   **Visualization**: Recharts (Radar/Area charts)
*   **State Management**: React Context (AuthProvider)

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js 18+
*   Google Gemini API Key

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
echo "SECRET_KEY=your_random_secret_string" >> .env

# Run server
uvicorn main:app --reload
```
*Backend runs on `http://localhost:8000`*

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```
*Frontend runs on `http://localhost:3000`*

## 📖 Usage Guide
1.  **Sign Up**: Create an account to save your progress.
2.  **Upload**: Upload a clear image of your syllabus or notes.
3.  **Take Quiz**: The first quiz will be an "Initial" assessment.
4.  **Review**: Check the detailed results page to learn from mistakes.
5.  **Adapt**: Continue with "Adaptive Quizzes" to challenge yourself with new questions at the appropriate difficulty level.
6.  **Track**: View the "Stats" dashboard to see your Bloom's Taxonomy radar chart and score history.

## 📄 License
This project is open-source and intended for educational purposes.
