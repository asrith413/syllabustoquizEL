# Syllabus to Quiz Platform

A platform that converts syllabus images into adaptive quiz modules using local AI models. Upload an image of any syllabus or topic list, and get intelligent MCQ quizzes tailored to your performance level.

## ✨ Features

- 📸 **Image Upload**: Upload syllabus/topic images (PNG, JPG, JPEG)
- 🔍 **OCR & Topic Extraction**: Automatically extracts text and identifies topics using EasyOCR
- 📝 **Quiz Generation**: Creates 15-20 MCQ questions based on extracted topics
- 🎯 **Adaptive Difficulty**: 
  - Low scores (<60%) → Easier follow-up quiz
  - High scores (≥80%) → Harder follow-up quiz
  - Medium scores → Moderate difficulty
- 📊 **Performance Analytics**: 
  - Score trends over time
  - Topic-wise performance charts
  - Average scores and statistics
- 🎨 **Clean UI**: Minimal, modern interface built with Tailwind CSS

## 🛠 Tech Stack

- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.8+
- **ML Models**: 
  - Phi-3-mini (local, free) for quiz generation
  - EasyOCR for text extraction from images
- **Database**: SQLite (lightweight, no setup required)
- **Charts**: Recharts for data visualization

## 🚀 Quick Start

### Option 1: Using Startup Scripts (macOS/Linux)

```bash
# Terminal 1 - Start Backend
./start_backend.sh

# Terminal 2 - Start Frontend  
./start_frontend.sh
```

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Backend runs on `http://localhost:8000`

#### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

## 📖 Usage

1. **Upload Image**: Go to `http://localhost:3000` and upload a syllabus image
2. **View Topics**: See automatically extracted topics from your image
3. **Take Initial Quiz**: Start with a 15-20 question MCQ test
4. **Get Results**: View your score and performance breakdown
5. **Adaptive Quiz**: Take a follow-up quiz adjusted to your performance level
6. **View Statistics**: Check your performance trends and topic-wise scores

## 🎯 How It Works

1. **Image Processing**: 
   - Uploaded image is processed using EasyOCR
   - Text is extracted and cleaned
   - Topics are identified using pattern matching

2. **Quiz Generation**:
   - Uses Phi-3-mini model (or rule-based fallback) to generate questions
   - Questions are tailored to extracted topics
   - Difficulty can be adjusted (easy/medium/hard)

3. **Adaptive Learning**:
   - Initial quiz is medium difficulty
   - Performance determines next quiz difficulty
   - System tracks all attempts and scores

4. **Analytics**:
   - All quiz attempts are stored
   - Performance charts show progress over time
   - Topic performance helps identify strengths/weaknesses

## 📋 Requirements

- Python 3.8+
- Node.js 18+
- 8GB+ RAM (for Phi-3 model, optional)
- 10GB+ disk space (for model download, optional)

## 🔧 Configuration

### Backend
- Default port: `8000`
- Database: `backend/quiz_data.db` (auto-created)
- Uploads: `backend/uploads/` (auto-created)

### Frontend
- Default port: `3000`
- API URL: Set `NEXT_PUBLIC_API_URL` in `.env.local` if different

## 🐛 Troubleshooting

See [SETUP.md](./SETUP.md) for detailed troubleshooting guide.

**Common Issues:**
- **Model download fails**: System automatically uses rule-based generation (works offline)
- **OCR not working**: Ensure image is clear and readable
- **Port conflicts**: Change ports in config files

## 📝 Notes

- **First Run**: Phi-3 model download (~7GB) happens automatically on first quiz generation
- **Offline Mode**: Rule-based quiz generation works without internet or model
- **Performance**: Phi-3 provides better questions but requires more resources

## 🎓 Example Use Cases

- Students preparing for exams
- Teachers creating practice quizzes
- Self-assessment and learning
- Topic review and reinforcement

## 📄 License

This project is open source and available for educational purposes.
