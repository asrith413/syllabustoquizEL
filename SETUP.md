# Setup Instructions

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- Internet connection (for first-time model download)

## Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note**: The first time you run the backend, it will attempt to download the Phi-3 model (~7GB). If this fails or you want to use rule-based generation (works offline), the system will automatically fall back.

4. Run the backend server:
```bash
python main.py
```

The backend will run on `http://localhost:8000`

## Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file (optional, defaults work):
```bash
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

4. Run the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Usage

1. Open `http://localhost:3000` in your browser
2. Upload an image of a syllabus or topic list
3. View extracted topics
4. Take the initial quiz (15-20 MCQs)
5. View your performance and take adaptive quizzes
6. Check your statistics dashboard

## Troubleshooting

### Model Download Issues
If Phi-3 model fails to download:
- The system automatically falls back to rule-based quiz generation
- Rule-based generation works offline and doesn't require the model
- To retry model download, ensure you have:
  - Stable internet connection
  - At least 10GB free disk space
  - Sufficient RAM (8GB+ recommended)

### OCR Issues
If text extraction fails:
- Ensure the image is clear and readable
- Try images with better contrast
- Supported formats: PNG, JPG, JPEG

### Port Conflicts
If ports 3000 or 8000 are in use:
- Change frontend port: `npm run dev -- -p 3001`
- Change backend port in `main.py`: `uvicorn.run(app, host="0.0.0.0", port=8001)`
