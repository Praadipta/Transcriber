from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
import shutil
import os
import uuid
from typing import Dict, Any, List
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

def format_srt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, remainder = divmod(millis, 3600 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"

def format_vtt_timestamp(seconds: float) -> str:
    millis = int(round(seconds * 1000))
    hours, remainder = divmod(millis, 3600 * 1000)
    minutes, remainder = divmod(remainder, 60 * 1000)
    secs, ms = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}.{ms:03}"

def segments_to_srt(segments: List[Dict[str, Any]]) -> str:
    lines: List[str] = []
    counter = 1
    for segment in segments:
        text = (segment.get("text") or "").strip()
        if not text:
            continue
        start = format_srt_timestamp(float(segment.get("start", 0.0)))
        end = format_srt_timestamp(float(segment.get("end", 0.0)))
        lines.extend([str(counter), f"{start} --> {end}", text, ""])
        counter += 1
    return "\n".join(lines).strip() + "\n"

def segments_to_vtt(segments: List[Dict[str, Any]]) -> str:
    lines: List[str] = ["WEBVTT", ""]
    for segment in segments:
        text = (segment.get("text") or "").strip()
        if not text:
            continue
        start = format_vtt_timestamp(float(segment.get("start", 0.0)))
        end = format_vtt_timestamp(float(segment.get("end", 0.0)))
        lines.extend([f"{start} --> {end}", text, ""])
    return "\n".join(lines).strip() + "\n"

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

@app.get("/download/{task_id}")
async def download_transcript(task_id: str, format: str = "txt"):
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    task = task_status[task_id]
    if task.get("status") != "completed":
        raise HTTPException(status_code=409, detail="Transcription not completed")

    text = task.get("result", "")
    segments = task.get("segments", [])
    fmt = format.lower()
    if fmt == "txt":
        content = text
        media_type = "text/plain"
        ext = "txt"
    elif fmt == "srt":
        if not segments:
            raise HTTPException(status_code=400, detail="No segments available")
        content = segments_to_srt(segments)
        media_type = "application/x-subrip"
        ext = "srt"
    elif fmt == "vtt":
        if not segments:
            raise HTTPException(status_code=400, detail="No segments available")
        content = segments_to_vtt(segments)
        media_type = "text/vtt"
        ext = "vtt"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")

    headers = {"Content-Disposition": f'attachment; filename="transcript_{task_id}.{ext}"'}
    return PlainTextResponse(content, media_type=media_type, headers=headers)

def process_transcription(task_id: str, file_path: str):
    try:
        task_status[task_id]["status"] = "transcribing"
        result = transcribe_video(file_path)
        task_status[task_id] = {
            "status": "completed",
            "result": result.get("text", ""),
            "segments": result.get("segments", []),
            "language": result.get("language"),
        }
    except Exception as e:
        task_status[task_id] = {"status": "failed", "error": str(e)}
    finally:
        # Cleanup file after processing if needed, or keep it
        # os.remove(file_path) 
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
