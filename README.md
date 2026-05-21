# Transcriber

A modern, fast video transcription app using a React + Vite frontend and a lightweight FastAPI backend.

The application has been upgraded to use the **Groq Whisper API** (`whisper-large-v3`), replacing the local PyTorch/Whisper installation. This results in significantly faster transcriptions, higher accuracy, and a tiny memory footprint for the backend, allowing it to be hosted on free serverless platforms.

## Architecture

- **Frontend:** React + Vite + TailwindCSS (Deployed on Vercel)
- **Backend:** Python + FastAPI (Deployed on Railway)
- **Transcription Engine:** Groq API (`whisper-large-v3`)

## Live Demo
- **App URL:** https://frontend-flax-rho-58.vercel.app
- **Backend API:** https://transcriber-production-39eb.up.railway.app

## Local Development Setup

### 1. Backend

1. Navigate to the `backend` directory.
2. Create and activate a virtual environment.
3. Install dependencies.
4. Set your Groq API key in the environment or `.env` file.
5. Run the FastAPI server.

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Set your Groq API key (get one at console.groq.com)
$env:GROQ_API_KEY="your-api-key"

python main.py
```
Backend runs at: `http://localhost:8000`

### 2. Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies.
3. Start the Vite dev server.

```powershell
cd frontend
npm install
npm run dev
```
Frontend runs at: `http://localhost:5173`

By default, the frontend connects to `http://localhost:8000`. You can change this by setting the `VITE_API_URL` environment variable.

## Deployment Notes

### Frontend (Vercel)
The frontend is built with Vite. It deploys natively to Vercel with zero configuration required. Simply set the `VITE_API_URL` environment variable to your production backend URL.

### Backend (Railway)
The backend is a standard FastAPI app. It requires the `GROQ_API_KEY` environment variable. The `Procfile` instructs Railway to run `python main.py`, which binds to the `PORT` environment variable injected by the platform.

Because it uses the Groq API instead of local ML models, the entire backend fits easily within the limits of free-tier hosting platforms (such as Railway, Render, or Koyeb) without running into memory or cold-start timeouts.

## License
MIT License
