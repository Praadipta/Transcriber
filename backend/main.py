from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
from typing import Dict
from transcriber import transcribe_video
import re

# Add local bin directory (where we put ffmpeg.exe) to PATH
bin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin")
os.environ["PATH"] += os.pathsep + bin_dir

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Store task status in memory (for simplicity, use a database for production)
task_status: Dict[str, Dict] = {}

import time

def sanitize_filename(filename: str) -> str:
    normalized = filename.replace("\\", "/")
    base = os.path.basename(normalized).strip().strip(".")
    if not base:
        base = "upload"
    return re.sub(r"[^A-Za-z0-9._-]", "_", base)

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    task_id = str(uuid.uuid4())
    safe_name = sanitize_filename(file.filename or "")
    file_location = os.path.join(UPLOAD_DIR, f"{task_id}_{safe_name}")
    upload_root = os.path.abspath(UPLOAD_DIR)
    file_path_abs = os.path.abspath(file_location)
    if not file_path_abs.startswith(upload_root + os.path.sep):
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Save the uploaded file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    task_status[task_id] = {
        "status": "processing", 
        "message": "File uploaded, starting transcription...",
        "start_time": time.time()
    }
    
    # Start transcription in background
    background_tasks.add_task(process_transcription, task_id, file_location)
    
    return {"task_id": task_id}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_status[task_id]

def process_transcription(task_id: str, file_path: str):
    try:
        task_status[task_id]["status"] = "transcribing"
        result = transcribe_video(file_path)
        task_status[task_id] = {"status": "completed", "result": result}
    except Exception as e:
        task_status[task_id] = {"status": "failed", "error": str(e)}
    finally:
        # Cleanup file after processing if needed, or keep it
        # os.remove(file_path) 
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
