# Transcriber

Simple video transcription app with a FastAPI backend and a Vite + React frontend.
Uploads a video, runs Whisper to generate text, and streams status updates.

## Requirements
- Python 3.8+
- Node.js 18+
- ffmpeg available on PATH (backend uses it via Whisper)

## Setup
1. Create and activate a Python virtual environment.
2. Install backend dependencies.
3. Install frontend dependencies.

Example:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r backend\requirements.txt

cd frontend
npm install
```

## Run (local dev)
Start both servers:
```bat
run_transcriber.bat
```

Manual start:
```powershell
cd backend
python main.py

cd ..\frontend
npm run dev -- --host
```

Backend: http://localhost:8000  
Frontend: http://localhost:5173

## Notes
- Uploaded files are stored in `backend/uploads/`.
- Long videos can take time; use the status endpoint to monitor progress.
- If `torch` fails to install on Windows, follow the official PyTorch install guide.
